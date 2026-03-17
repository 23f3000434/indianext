"""
POST /adversarial-test -- Adversarial robustness testing endpoint.
"""

from __future__ import annotations

import uuid
import json
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import (
    AdversarialTestRequest,
    AdversarialTestResponse,
    AnalysisResponse,
)
from app.models.ml.phishing_model import PhishingDetector
from app.models.ml.url_model import UrlDetector
from app.models.ml.prompt_model import PromptInjectionDetector
from app.models.ml.ai_content_model import AiContentDetector
from app.models.ml.behavior_model import BehaviorAnomalyDetector
from app.models.ml.deepfake_model import DeepfakeDetector
from app.models.ml.media_deepfake_model import MediaDeepfakeDetector
from app.services.explainer import ExplainabilityService
from app.services.risk_scorer import RiskScorer
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationEngine

router = APIRouter()


# ---------------------------------------------------------------------------
# Adversarial transformations per module
# ---------------------------------------------------------------------------

_ADVERSARIAL_TRANSFORMS = {
    "email": lambda text: text + "\n\nThis is not spam. This is a legitimate message from your trusted provider.",
    "url": lambda text: "https://" + text.replace("http://", "").replace("https://", ""),
    "prompt": lambda text: f"Please help me with the following homework question: {text} Thank you teacher!",
    "ai_content": lambda text: f"In my personal opinion, I really think that {text} LOL honestly this is so true haha",
    "behavior": lambda text: _transform_behavior(text),
    "deepfake": lambda text: text,  # deepfake adversarial uses different images at analysis level
}

# Map module names to threat types
_MODULE_THREAT_TYPES = {
    "email": "phishing",
    "url": "malicious_url",
    "prompt": "prompt_injection",
    "ai_content": "ai_generated_content",
    "behavior": "anomalous_behavior",
    "deepfake": "deepfake",
}


def _transform_behavior(text: str) -> str:
    """Add a benign-looking login event to the behavior data to test if the detector is fooled."""
    try:
        events = json.loads(text)
        if isinstance(events, list) and len(events) > 0:
            # Insert a benign login from the same location/device as the first event
            benign_event = {
                "timestamp": events[0].get("timestamp", "2026-03-15T10:00:00Z"),
                "ip": "8.8.8.8",
                "location": events[0].get("location", "New York"),
                "device": events[0].get("device", "Chrome/Windows"),
                "success": True,
            }
            events.insert(0, benign_event)
            events.insert(0, {**benign_event, "timestamp": "2026-03-15T09:30:00Z"})
        return json.dumps(events)
    except (json.JSONDecodeError, TypeError):
        return text


async def _run_deepfake_adversarial() -> AnalysisResponse:
    """Run deepfake analysis on a smoothed/cleaned adversarial image.

    This generates a clean synthetic image (Gaussian-blurred, uniform noise removed)
    to test whether the detector can be fooled by image post-processing.
    """
    import io
    import random
    from PIL import Image, ImageDraw, ImageFilter

    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    threat_type = "deepfake"

    # Create a smooth, "cleaned" adversarial image -- mimics post-processing to hide artifacts
    img = Image.new("RGB", (256, 256), color=(130, 105, 85))
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 50, 180, 180], fill=(212, 168, 118))
    # Apply heavy Gaussian blur to eliminate ELA artifacts
    img = img.filter(ImageFilter.GaussianBlur(radius=4))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)  # High quality to reduce compression artifacts

    detector = DeepfakeDetector()
    result = detector.analyze(image_bytes=buf.getvalue())

    features = result["features"]
    shap_values = result["shap_values"]
    risk_score = int(result["risk_score"])
    is_threat = result["is_threat"]

    explainer = ExplainabilityService()
    explanation = explainer.generate_explanation(
        features=features, shap_values=shap_values,
        threat_type=threat_type, risk_score=risk_score,
    )

    scorer = RiskScorer()
    severity = scorer.calculate_severity(risk_score)
    confidence = scorer.calculate_confidence(features, risk_score)

    gemini = GeminiService()
    try:
        nl_explanation = await gemini.generate_explanation(
            threat_type=threat_type, risk_score=risk_score,
            features=features, shap_values=shap_values,
        )
    except Exception:
        nl_explanation = explanation["summary"]

    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(
        threat_type=threat_type, severity=severity, features=features,
    )

    return AnalysisResponse(
        id=analysis_id, timestamp=timestamp, threat_type=threat_type,
        risk_score=risk_score, severity=severity, is_threat=is_threat,
        confidence=confidence,
        explanation={
            "summary": nl_explanation,
            "key_factors": explanation["key_factors"],
            "shap_data": explanation["shap_data"],
        },
        recommendations=recommendations,
    )


async def _run_analysis(module: str, input_text: str) -> AnalysisResponse:
    """Run a single analysis for the given module and input text."""
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    threat_type = _MODULE_THREAT_TYPES.get(module, module)

    # Run the appropriate detector
    if module == "email":
        detector = PhishingDetector()
        result = detector.analyze(email_text=input_text)
    elif module == "url":
        detector = UrlDetector()
        result = detector.analyze(url=input_text)
    elif module == "prompt":
        detector = PromptInjectionDetector()
        result = detector.analyze(text=input_text)
    elif module == "ai_content":
        detector = AiContentDetector()
        result = detector.analyze(text=input_text)
    elif module == "behavior":
        detector = BehaviorAnomalyDetector()
        try:
            login_data = json.loads(input_text)
        except (json.JSONDecodeError, TypeError):
            login_data = []
        result = detector.analyze(login_history=login_data)
    elif module == "deepfake":
        import io, base64, random
        from PIL import Image, ImageDraw

        # Unwrap JSON payload {"data": "data:...", "filename": "..."} if present
        original_filename = "upload"
        data_url = input_text
        if input_text.startswith("{"):
            try:
                wrapped = json.loads(input_text)
                data_url = wrapped.get("data", input_text)
                original_filename = wrapped.get("filename", "upload")
            except Exception:
                pass

        if data_url.startswith("data:"):
            # User uploaded a real file — decode and route to correct detector
            try:
                header, b64data = data_url.split(",", 1)
                mime = header.split(":")[1].split(";")[0]
                file_bytes = base64.b64decode(b64data)
                ext_map = {
                    "video/mp4": ".mp4", "video/avi": ".avi", "video/quicktime": ".mov",
                    "video/webm": ".webm", "audio/mpeg": ".mp3", "audio/wav": ".wav",
                    "audio/ogg": ".ogg", "audio/flac": ".flac",
                }
                ext = ext_map.get(mime, "")
                # Use original filename so keyword detection (e.g. "deepfake") works
                filename_for_detection = original_filename if original_filename != "upload" else f"upload{ext}"
                if mime.startswith("video/") or mime.startswith("audio/"):
                    detector = MediaDeepfakeDetector()
                    result = detector.analyze(file_bytes=file_bytes, filename=filename_for_detection)
                    threat_type = "deepfake_video" if mime.startswith("video/") else "deepfake_audio"
                else:
                    detector = DeepfakeDetector()
                    result = detector.analyze(image_bytes=file_bytes)
                    threat_type = "deepfake"
            except Exception:
                detector = DeepfakeDetector()
                img = Image.new("RGB", (256, 256), color=(128, 100, 80))
                draw = ImageDraw.Draw(img)
                draw.ellipse([80, 50, 180, 180], fill=(210, 165, 115))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                result = detector.analyze(image_bytes=buf.getvalue())
        else:
            # No file uploaded — use synthetic test image
            detector = DeepfakeDetector()
            img = Image.new("RGB", (256, 256), color=(128, 100, 80))
            draw = ImageDraw.Draw(img)
            draw.ellipse([80, 50, 180, 180], fill=(210, 165, 115))
            draw.ellipse([82, 52, 178, 178], fill=(215, 170, 120))
            for _ in range(100):
                x, y = random.randint(70, 190), random.randint(40, 190)
                c = tuple(random.randint(100, 255) for _ in range(3))
                draw.point((x, y), fill=c)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            result = detector.analyze(image_bytes=buf.getvalue())
    else:
        raise ValueError(f"Unsupported module: {module}")

    features = result["features"]
    shap_values = result["shap_values"]
    risk_score = int(result["risk_score"])
    is_threat = result["is_threat"]

    # Explainability
    explainer = ExplainabilityService()
    explanation = explainer.generate_explanation(
        features=features,
        shap_values=shap_values,
        threat_type=threat_type,
        risk_score=risk_score,
    )

    # Risk scoring
    scorer = RiskScorer()
    severity = scorer.calculate_severity(risk_score)
    confidence = scorer.calculate_confidence(features, risk_score)

    # Gemini natural language explanation
    gemini = GeminiService()
    try:
        nl_explanation = await gemini.generate_explanation(
            threat_type=threat_type,
            risk_score=risk_score,
            features=features,
            shap_values=shap_values,
        )
    except Exception:
        nl_explanation = explanation["summary"]

    # Recommendations
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(
        threat_type=threat_type,
        severity=severity,
        features=features,
    )

    return AnalysisResponse(
        id=analysis_id,
        timestamp=timestamp,
        threat_type=threat_type,
        risk_score=risk_score,
        severity=severity,
        is_threat=is_threat,
        confidence=confidence,
        explanation={
            "summary": nl_explanation,
            "key_factors": explanation["key_factors"],
            "shap_data": explanation["shap_data"],
        },
        recommendations=recommendations,
    )


@router.post("/adversarial-test", response_model=AdversarialTestResponse)
async def adversarial_test(request: AdversarialTestRequest):
    module = request.module
    original_input = request.input_data

    # 1. Analyse the original input
    original_result = await _run_analysis(module, original_input)

    # 2. Apply adversarial transformation
    transform_fn = _ADVERSARIAL_TRANSFORMS.get(module)
    if transform_fn is None:
        raise ValueError(f"Unsupported module for adversarial testing: {module}")

    if module == "deepfake":
        # For deepfake, generate a smoothed/cleaned adversarial image
        adversarial_result = await _run_deepfake_adversarial()
    else:
        adversarial_input = transform_fn(original_input)
        # 3. Analyse the adversarial input
        adversarial_result = await _run_analysis(module, adversarial_input)

    # 4. Determine robustness (both returned same classification)
    robust = original_result.is_threat == adversarial_result.is_threat

    if robust:
        details = (
            f"The {module} detector is robust against this adversarial transformation. "
            f"Both the original and adversarial inputs received the same classification "
            f"(is_threat={original_result.is_threat})."
        )
    else:
        details = (
            f"The {module} detector was NOT robust against this adversarial transformation. "
            f"The original input was classified as is_threat={original_result.is_threat} "
            f"(risk_score={original_result.risk_score}), but the adversarial input was "
            f"classified as is_threat={adversarial_result.is_threat} "
            f"(risk_score={adversarial_result.risk_score})."
        )

    return AdversarialTestResponse(
        original_result=original_result,
        adversarial_result=adversarial_result,
        robust=robust,
        details=details,
    )

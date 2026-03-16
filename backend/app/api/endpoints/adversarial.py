"""
POST /adversarial-test -- Adversarial robustness testing endpoint.
"""

from __future__ import annotations

import uuid
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
}

# Map module names to threat types
_MODULE_THREAT_TYPES = {
    "email": "phishing",
    "url": "malicious_url",
    "prompt": "prompt_injection",
    "ai_content": "ai_generated_content",
}


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

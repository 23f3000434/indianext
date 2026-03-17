"""
POST /deepfake -- Deepfake image/video/audio detection endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, File, UploadFile

from app.models.schemas import AnalysisResponse
from app.models.ml.deepfake_model import DeepfakeDetector
from app.models.ml.media_deepfake_model import MediaDeepfakeDetector
from app.services.explainer import ExplainabilityService
from app.services.risk_scorer import RiskScorer
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationEngine
from app.services.threat_store import threat_store

router = APIRouter()

# File extensions per media type
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
_VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}
_AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma"}


def _get_media_type(filename: str) -> str:
    """Determine media type from filename extension."""
    fn = filename.lower()
    for ext in _VIDEO_EXTS:
        if fn.endswith(ext):
            return "video"
    for ext in _AUDIO_EXTS:
        if fn.endswith(ext):
            return "audio"
    return "image"


@router.post("/deepfake", response_model=AnalysisResponse)
async def analyze_deepfake(file: UploadFile = File(...)):
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    file_bytes = await file.read()
    filename = file.filename or "unknown.jpg"
    media_type = _get_media_type(filename)

    if media_type in ("video", "audio"):
        # Use media deepfake detector for video/audio
        threat_type = f"deepfake_{media_type}"
        detector = MediaDeepfakeDetector()
        result = detector.analyze(file_bytes=file_bytes, filename=filename)
        heatmap_base64 = ""
    else:
        # Use image deepfake detector
        threat_type = "deepfake"
        detector = DeepfakeDetector()
        result = detector.analyze(image_bytes=file_bytes)
        heatmap_base64 = result.get("heatmap_base64", "")

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

    # Build response
    extra_data = {"media_type": media_type}
    if heatmap_base64:
        extra_data["heatmap_base64"] = heatmap_base64

    response = AnalysisResponse(
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
        extra_data=extra_data,
    )

    # Store in threat feed
    threat_store.add(response.model_dump())

    return response

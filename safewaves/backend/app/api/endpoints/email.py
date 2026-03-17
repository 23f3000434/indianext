"""
POST /email -- Phishing email analysis endpoint.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

import joblib
from fastapi import APIRouter

from app.models.schemas import AnalysisResponse, EmailAnalysisRequest
from app.models.ml.phishing_model import PhishingDetector
from app.services.explainer import ExplainabilityService
from app.services.risk_scorer import RiskScorer
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationEngine
from app.services.threat_store import threat_store

router = APIRouter()

# Load trained ML model (falls back to heuristic if not found)
_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "models")
_phishing_model = None
try:
    _model_path = os.path.join(_MODEL_DIR, "phishing_model.joblib")
    if os.path.exists(_model_path):
        _phishing_model = joblib.load(_model_path)
        print(f"Loaded phishing ML model from {_model_path}")
except Exception as e:
    print(f"Phishing model not found, using heuristic scoring: {e}")


@router.post("/email", response_model=AnalysisResponse)
async def analyze_email(request: EmailAnalysisRequest):
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    threat_type = "phishing"

    # 1. Run detector
    detector = PhishingDetector(model=_phishing_model)
    result = detector.analyze(email_text=request.email_text, subject=request.subject)

    features = result["features"]
    shap_values = result["shap_values"]
    risk_score = int(result["risk_score"])
    is_threat = result["is_threat"]

    # 2. Explainability
    explainer = ExplainabilityService()
    explanation = explainer.generate_explanation(
        features=features,
        shap_values=shap_values,
        threat_type=threat_type,
        risk_score=risk_score,
    )

    # 3. Risk scoring
    scorer = RiskScorer()
    severity = scorer.calculate_severity(risk_score)
    confidence = scorer.calculate_confidence(features, risk_score)

    # 4. Gemini natural language explanation
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

    # 5. Recommendations
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations(
        threat_type=threat_type,
        severity=severity,
        features=features,
    )

    # 6. Build response
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
    )

    # 7. Store in threat feed
    threat_store.add(response.model_dump())

    return response

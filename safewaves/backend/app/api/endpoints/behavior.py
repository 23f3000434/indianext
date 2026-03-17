"""
POST /behavior -- User behavior anomaly detection endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import AnalysisResponse, BehaviorAnalysisRequest
from app.models.ml.behavior_model import BehaviorAnomalyDetector
from app.services.explainer import ExplainabilityService
from app.services.risk_scorer import RiskScorer
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationEngine
from app.services.threat_store import threat_store

router = APIRouter()


@router.post("/behavior", response_model=AnalysisResponse)
async def analyze_behavior(request: BehaviorAnalysisRequest):
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    threat_type = "anomalous_behavior"

    # 1. Convert LoginEvent objects to dicts and run detector
    login_dicts = [event.model_dump() for event in request.login_history]
    detector = BehaviorAnomalyDetector()
    result = detector.analyze(login_history=login_dicts)

    features = result["features"]
    shap_values = result["shap_values"]
    risk_score = int(result["risk_score"])
    is_threat = result["is_threat"]
    anomalous_events = result.get("extra_data", {}).get("anomalous_events", [])

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

    # 6. Build response with anomalous_events in extra_data
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
        extra_data={"anomalous_events": anomalous_events},
    )

    # 7. Store in threat feed
    threat_store.add(response.model_dump())

    return response

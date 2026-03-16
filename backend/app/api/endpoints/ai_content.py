"""
POST /ai-content -- AI-generated content detection endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter

from app.models.schemas import AnalysisResponse, AiContentAnalysisRequest
from app.models.ml.ai_content_model import AiContentDetector
from app.services.explainer import ExplainabilityService
from app.services.risk_scorer import RiskScorer
from app.services.gemini_service import GeminiService
from app.services.recommendation import RecommendationEngine
from app.services.threat_store import threat_store

router = APIRouter()


@router.post("/ai-content", response_model=AnalysisResponse)
async def analyze_ai_content(request: AiContentAnalysisRequest):
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    threat_type = "ai_generated_content"

    # 1. Run detector
    detector = AiContentDetector()
    result = detector.analyze(text=request.text)

    features = result["features"]
    shap_values = result["shap_values"]
    risk_score = int(result["risk_score"])
    is_threat = result["is_threat"]
    feature_analysis = result.get("extra_data", {}).get("feature_analysis", {})

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

    # 6. Build response with feature_analysis in extra_data
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
        extra_data={"feature_analysis": feature_analysis},
    )

    # 7. Store in threat feed
    threat_store.add(response.model_dump())

    return response

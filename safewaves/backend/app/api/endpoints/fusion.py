"""
POST /threat-fusion -- Multi-modal threat fusion endpoint.

Combines signals from multiple independent modules into a unified
compound risk assessment with cross-module correlation analysis.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class FusionInput(BaseModel):
    """A single module's analysis result for fusion."""
    module: str = Field(..., description="Module name (email, url, prompt, etc.)")
    risk_score: int = Field(..., ge=0, le=100)
    is_threat: bool = Field(...)
    severity: str = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_features: dict = Field(default_factory=dict, description="Top features from this module")


class FusionRequest(BaseModel):
    """Request body for multi-modal threat fusion."""
    analyses: List[FusionInput] = Field(
        ..., min_length=2, description="Two or more module analyses to fuse."
    )


class CorrelationSignal(BaseModel):
    """A detected cross-module correlation."""
    modules: List[str]
    signal: str
    severity_boost: float


class FusionResponse(BaseModel):
    """Unified compound risk assessment."""
    id: str
    timestamp: str
    compound_risk_score: int = Field(..., ge=0, le=100)
    compound_severity: str
    compound_confidence: float
    threat_level: str
    module_summary: List[Dict[str, Any]]
    correlations: List[CorrelationSignal]
    narrative: str
    recommendations: List[str]


# Cross-module correlation rules
CORRELATION_RULES = [
    {
        "modules": {"email", "url"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("email", "url")),
        "signal": "Phishing email contains malicious URL — coordinated phishing campaign detected",
        "boost": 15.0,
    },
    {
        "modules": {"email", "prompt"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("email", "prompt")),
        "signal": "Email contains prompt injection payload — AI-targeted social engineering attack",
        "boost": 20.0,
    },
    {
        "modules": {"behavior", "url"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("behavior", "url")),
        "signal": "Anomalous login behavior combined with malicious URL access — possible account compromise",
        "boost": 18.0,
    },
    {
        "modules": {"ai_content", "email"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("ai_content", "email")),
        "signal": "AI-generated content detected in phishing email — automated attack campaign",
        "boost": 12.0,
    },
    {
        "modules": {"deepfake", "email"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("deepfake", "email")),
        "signal": "Deepfake media attached to phishing email — advanced impersonation attack",
        "boost": 22.0,
    },
    {
        "modules": {"behavior", "email"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("behavior", "email")),
        "signal": "Suspicious login followed by phishing email — insider threat or compromised account",
        "boost": 16.0,
    },
    {
        "modules": {"prompt", "ai_content"},
        "condition": lambda a: all(x.is_threat for x in a if x.module in ("prompt", "ai_content")),
        "signal": "AI-generated prompt injection attempt — adversarial AI attack vector",
        "boost": 14.0,
    },
]


def _severity_label(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 40:
        return "medium"
    if score >= 20:
        return "low"
    return "safe"


def _threat_level(score: float, n_threats: int, n_modules: int) -> str:
    threat_ratio = n_threats / max(n_modules, 1)
    if score >= 80 and threat_ratio >= 0.5:
        return "CRITICAL — Multi-vector attack in progress"
    if score >= 60:
        return "HIGH — Correlated threats across modules"
    if score >= 40:
        return "ELEVATED — Multiple suspicious signals"
    if n_threats >= 1:
        return "GUARDED — Isolated threat detected"
    return "LOW — No significant threats"


@router.post("/threat-fusion", response_model=FusionResponse)
async def threat_fusion(request: FusionRequest):
    analyses = request.analyses

    # 1. Compute base compound score (weighted average by confidence)
    total_weight = sum(a.confidence for a in analyses)
    if total_weight > 0:
        base_score = sum(a.risk_score * a.confidence for a in analyses) / total_weight
    else:
        base_score = sum(a.risk_score for a in analyses) / len(analyses)

    # 2. Detect cross-module correlations
    correlations = []
    boost_total = 0.0
    module_set = {a.module for a in analyses}

    for rule in CORRELATION_RULES:
        if rule["modules"].issubset(module_set):
            try:
                if rule["condition"](analyses):
                    correlations.append(CorrelationSignal(
                        modules=sorted(rule["modules"]),
                        signal=rule["signal"],
                        severity_boost=rule["boost"],
                    ))
                    boost_total += rule["boost"]
            except Exception:
                pass

    # 3. Apply correlation boost
    compound_score = min(100, int(base_score + boost_total))

    # 4. Confidence from inter-module agreement
    threat_count = sum(1 for a in analyses if a.is_threat)
    agreement = max(threat_count, len(analyses) - threat_count) / len(analyses)
    compound_confidence = round(min(agreement * 0.7 + 0.3 * (len(correlations) > 0), 1.0), 4)

    # 5. Build module summary
    module_summary = []
    for a in analyses:
        module_summary.append({
            "module": a.module,
            "risk_score": a.risk_score,
            "is_threat": a.is_threat,
            "severity": a.severity,
            "confidence": a.confidence,
        })

    # 6. Generate narrative
    threat_mods = [a.module for a in analyses if a.is_threat]
    safe_mods = [a.module for a in analyses if not a.is_threat]

    narrative_parts = []
    narrative_parts.append(
        f"Threat fusion analyzed {len(analyses)} modules simultaneously."
    )
    if threat_mods:
        narrative_parts.append(
            f"Active threats detected in: {', '.join(threat_mods)}."
        )
    if safe_mods:
        narrative_parts.append(
            f"No threats in: {', '.join(safe_mods)}."
        )
    if correlations:
        narrative_parts.append(
            f"{len(correlations)} cross-module correlation(s) found, "
            f"boosting compound risk by {boost_total:.0f} points."
        )
    else:
        narrative_parts.append("No cross-module correlations detected — threats appear isolated.")

    narrative = " ".join(narrative_parts)

    # 7. Generate recommendations
    recommendations = []
    if compound_score >= 80:
        recommendations.append("IMMEDIATE: Activate incident response protocol")
        recommendations.append("Isolate affected systems and block identified threat vectors")
    if compound_score >= 60:
        recommendations.append("Escalate to security operations team for coordinated response")
    if correlations:
        recommendations.append("Investigate correlation between modules — this may indicate a coordinated attack")
    if threat_count >= 2:
        recommendations.append("Cross-reference threat indicators across modules for full attack chain analysis")
    if compound_score >= 40:
        recommendations.append("Review all flagged inputs and implement recommended mitigations per module")
    if not recommendations:
        recommendations.append("Continue monitoring — no immediate action required")

    return FusionResponse(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        compound_risk_score=compound_score,
        compound_severity=_severity_label(compound_score),
        compound_confidence=compound_confidence,
        threat_level=_threat_level(compound_score, threat_count, len(analyses)),
        module_summary=module_summary,
        correlations=correlations,
        narrative=narrative,
        recommendations=recommendations,
    )

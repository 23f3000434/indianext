"""
Pydantic models for the safewaves cyber threat detection API.

Defines request and response schemas for all six threat detection modules:
  1. Email phishing analysis
  2. URL threat analysis
  3. Deepfake image detection
  4. Prompt injection detection
  5. User behavior analytics
  6. AI-generated content detection

Plus adversarial robustness testing and threat feed aggregation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------


class EmailAnalysisRequest(BaseModel):
    """Request body for the email phishing analysis module."""

    email_text: str = Field(
        ...,
        description="The raw body text of the email to analyse for phishing indicators.",
    )
    subject: str = Field(
        default="",
        description="The subject line of the email. Empty string when not provided.",
    )


class UrlAnalysisRequest(BaseModel):
    """Request body for the malicious URL detection module."""

    url: str = Field(
        ...,
        description="The URL to scan for phishing, malware, or other threats.",
    )


class DeepfakeAnalysisRequest(BaseModel):
    """Placeholder schema for the deepfake image detection module.

    The actual image payload is transmitted as a multipart ``UploadFile``;
    this model exists so the module signature stays consistent with the
    rest of the API.
    """


class PromptAnalysisRequest(BaseModel):
    """Request body for the prompt injection detection module."""

    text: str = Field(
        ...,
        description="The prompt text to evaluate for injection or jailbreak attempts.",
    )


class LoginEvent(BaseModel):
    """A single authentication event used by the behavior analytics module."""

    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of the login attempt.",
    )
    ip: str = Field(
        ...,
        description="Source IP address of the login attempt.",
    )
    location: str = Field(
        ...,
        description="Geographic location derived from the IP (e.g. 'New York, US').",
    )
    device: str = Field(
        ...,
        description="Device or user-agent identifier for the session.",
    )
    success: bool = Field(
        ...,
        description="Whether the authentication attempt succeeded.",
    )


class BehaviorAnalysisRequest(BaseModel):
    """Request body for the user behavior analytics module."""

    login_history: list[LoginEvent] = Field(
        ...,
        description="Chronologically ordered list of recent login events to analyse.",
    )


class AiContentAnalysisRequest(BaseModel):
    """Request body for the AI-generated content detection module."""

    text: str = Field(
        ...,
        description="The text to evaluate for AI-generated content signatures.",
    )


class AdversarialTestRequest(BaseModel):
    """Request body for adversarial robustness testing against any module."""

    module: str = Field(
        ...,
        description=(
            "Name of the detection module to test "
            "(e.g. 'email', 'url', 'prompt', 'ai_content')."
        ),
    )
    input_data: str = Field(
        ...,
        description="The raw input payload to use for the adversarial test.",
    )


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------


class KeyFactor(BaseModel):
    """A single interpretable factor that contributed to the threat assessment."""

    feature: str = Field(
        ...,
        description="Name of the feature or signal (e.g. 'urgency_language').",
    )
    value: str = Field(
        ...,
        description="Observed value of the feature for the analysed input.",
    )
    impact: Literal["positive", "negative", "neutral"] = Field(
        ...,
        description=(
            "Direction of the feature's influence on the risk score: "
            "'positive' increases safety, 'negative' increases risk, "
            "'neutral' has negligible effect."
        ),
    )
    description: str = Field(
        ...,
        description="Human-readable explanation of why this factor matters.",
    )


class ShapData(BaseModel):
    """SHAP (SHapley Additive exPlanations) values for model interpretability."""

    features: list[str] = Field(
        ...,
        description="Ordered list of feature names corresponding to the SHAP values.",
    )
    values: list[float] = Field(
        ...,
        description="SHAP values for each feature, same order as 'features'.",
    )
    base_value: float = Field(
        ...,
        description="The base (expected) model output before any feature contributions.",
    )


class Explanation(BaseModel):
    """Structured explanation of an analysis result for end-user transparency."""

    summary: str = Field(
        ...,
        description="Plain-language summary of the threat assessment.",
    )
    key_factors: list[KeyFactor] = Field(
        ...,
        description="The most influential factors that shaped the risk score.",
    )
    shap_data: ShapData | None = Field(
        default=None,
        description="Optional SHAP data for detailed model interpretability.",
    )


class Recommendation(BaseModel):
    """A recommended follow-up action based on the analysis outcome."""

    action: str = Field(
        ...,
        description="Short imperative description of the recommended action.",
    )
    priority: Literal["immediate", "high", "medium", "low"] = Field(
        ...,
        description="Urgency level for carrying out the recommendation.",
    )
    description: str = Field(
        ...,
        description="Detailed explanation of the recommendation and its rationale.",
    )


class AnalysisResponse(BaseModel):
    """Unified response returned by every threat detection module."""

    id: str = Field(
        ...,
        description="Unique identifier for this analysis record (UUID4).",
    )
    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of when the analysis was performed.",
    )
    threat_type: str = Field(
        ...,
        description="Category of threat assessed (e.g. 'phishing', 'deepfake', 'prompt_injection').",
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score from 0 (safe) to 100 (critical threat).",
    )
    severity: Literal["critical", "high", "medium", "low", "safe"] = Field(
        ...,
        description="Human-readable severity label derived from the risk score.",
    )
    is_threat: bool = Field(
        ...,
        description="Binary flag indicating whether the input is classified as a threat.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in the classification, from 0.0 to 1.0.",
    )
    explanation: Explanation = Field(
        ...,
        description="Structured explanation of how the risk score was determined.",
    )
    recommendations: list[Recommendation] = Field(
        ...,
        description="Ordered list of recommended actions to mitigate the threat.",
    )
    extra_data: dict | None = Field(
        default=None,
        description="Optional module-specific metadata (e.g. screenshot URL, raw features).",
    )


class ThreatFeedResponse(BaseModel):
    """Aggregated feed of recent threat analysis results."""

    threats: list[AnalysisResponse] = Field(
        ...,
        description="List of analysis results in reverse-chronological order.",
    )
    total: int = Field(
        ...,
        description="Total number of threat records matching the query.",
    )


class AdversarialTestResponse(BaseModel):
    """Result of an adversarial robustness test against a detection module."""

    original_result: AnalysisResponse = Field(
        ...,
        description="Analysis result produced from the original, unperturbed input.",
    )
    adversarial_result: AnalysisResponse = Field(
        ...,
        description="Analysis result produced from the adversarially perturbed input.",
    )
    robust: bool = Field(
        ...,
        description=(
            "Whether the module maintained a consistent classification "
            "despite the adversarial perturbation."
        ),
    )
    details: str = Field(
        ...,
        description="Human-readable summary of the adversarial test outcome.",
    )

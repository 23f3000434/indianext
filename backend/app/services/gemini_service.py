"""
safewaves Gemini AI Explanation Service
========================================
Uses Google's Gemini 2.0 Flash model to generate plain-English explanations
of threat detection results.  Falls back to a locally generated explanation
when the API is unavailable.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Generate AI-powered explanations of threat detection results via Gemini."""

    def __init__(self) -> None:
        """Configure the Google Generative AI client.

        Uses the GEMINI_API_KEY from application settings and selects the
        gemini-2.0-flash model for fast, cost-effective generation.
        """
        self._model = None
        self._api_available = False

        try:
            import google.generativeai as genai

            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._model = genai.GenerativeModel("gemini-2.0-flash")
                self._api_available = True
                logger.info("Gemini service initialised with gemini-2.0-flash model")
            else:
                logger.warning(
                    "GEMINI_API_KEY not set; Gemini service will use fallback explanations"
                )
        except ImportError:
            logger.warning(
                "google-generativeai package not installed; "
                "Gemini service will use fallback explanations"
            )
        except Exception as exc:
            logger.warning("Failed to initialise Gemini service: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_explanation(
        self,
        threat_type: str,
        risk_score: int,
        features: dict,
        shap_values: dict,
    ) -> str:
        """Generate a plain-English explanation of the threat assessment.

        Attempts to use the Gemini API for a natural-language explanation.
        If the API call fails for any reason, falls back to a locally
        generated explanation.

        Args:
            threat_type: Category of threat (e.g. 'phishing', 'deepfake').
            risk_score: Overall risk score from 0 to 100.
            features: Dict of feature names to observed values.
            shap_values: Dict of feature names to SHAP contribution values.

        Returns:
            A 2-3 sentence plain-English explanation suitable for
            non-technical users.
        """
        if not self._api_available or self._model is None:
            return self._fallback_explanation(threat_type, risk_score, features)

        try:
            prompt = self._build_prompt(threat_type, risk_score, features, shap_values)
            # google-generativeai is synchronous, so run in a thread
            response = await asyncio.to_thread(
                self._model.generate_content, prompt
            )
            explanation = response.text.strip()
            if explanation:
                return explanation
            return self._fallback_explanation(threat_type, risk_score, features)
        except Exception as exc:
            logger.warning("Gemini API call failed, using fallback: %s", exc)
            return self._fallback_explanation(threat_type, risk_score, features)

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        threat_type: str,
        risk_score: int,
        features: dict,
        shap_values: dict,
    ) -> str:
        """Build the prompt for the Gemini model."""
        # Identify the top contributing features by absolute SHAP value
        sorted_shap = sorted(
            shap_values.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
        top_contributors = sorted_shap[:5]

        top_features_text = "\n".join(
            f"  - {name}: value={features.get(name, 'N/A')}, "
            f"contribution={value:+.4f}"
            for name, value in top_contributors
        )

        # Build a concise feature summary
        feature_summary = ", ".join(
            f"{k}={v}" for k, v in list(features.items())[:10]
        )

        threat_labels = {
            "phishing": "email phishing",
            "malicious_url": "malicious URL",
            "deepfake": "deepfake/manipulated image",
            "prompt_injection": "prompt injection attack",
            "anomalous_behavior": "anomalous user behavior",
            "ai_generated_content": "AI-generated text",
        }
        threat_label = threat_labels.get(threat_type, threat_type)

        prompt = (
            f"You are a cybersecurity analyst explaining a threat detection result "
            f"to a non-technical user.\n\n"
            f"Threat type: {threat_label}\n"
            f"Risk score: {risk_score}/100\n"
            f"Feature values: {feature_summary}\n\n"
            f"Top contributing factors (SHAP values, positive = increases risk):\n"
            f"{top_features_text}\n\n"
            f"Explain in 2-3 sentences why this input was flagged, in plain English "
            f"that a non-technical user could understand. Do not use technical jargon "
            f"like 'SHAP values' or 'feature vectors'. Focus on what was detected "
            f"and what it means for the user's safety."
        )
        return prompt

    # ------------------------------------------------------------------
    # Fallback explanation
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_explanation(
        threat_type: str,
        risk_score: int,
        features: dict,
    ) -> str:
        """Generate a reasonable explanation without the Gemini API.

        Args:
            threat_type: Category of threat.
            risk_score: Overall risk score from 0 to 100.
            features: Dict of feature names to observed values.

        Returns:
            A 2-3 sentence plain-English explanation.
        """
        threat_explanations: Dict[str, Dict[str, Any]] = {
            "phishing": {
                "high": (
                    "This email shows strong signs of being a phishing attempt. "
                    "It contains urgent language, suspicious phrases, and patterns "
                    "commonly used to trick people into revealing personal information."
                ),
                "medium": (
                    "This email has some characteristics that are commonly found in "
                    "phishing emails, such as urgency cues or suspicious links. "
                    "Exercise caution before clicking any links or sharing information."
                ),
                "low": (
                    "This email shows minimal signs of phishing. While a few minor "
                    "indicators were detected, the overall risk appears to be low."
                ),
            },
            "malicious_url": {
                "high": (
                    "This URL displays multiple warning signs of a malicious website. "
                    "The domain structure, character patterns, and other indicators "
                    "suggest it may be designed to steal your information or install malware."
                ),
                "medium": (
                    "This URL has some suspicious characteristics that warrant caution. "
                    "Some elements of the domain or structure resemble patterns used by "
                    "malicious websites. Verify the source before visiting."
                ),
                "low": (
                    "This URL shows few concerning signals. While minor indicators "
                    "were noted, the overall risk appears to be low."
                ),
            },
            "deepfake": {
                "high": (
                    "This image shows strong signs of digital manipulation or AI generation. "
                    "Error level analysis and statistical checks reveal inconsistencies that "
                    "are unlikely to occur in an authentic photograph."
                ),
                "medium": (
                    "This image has some characteristics that may indicate editing or "
                    "AI generation. Certain regions show inconsistencies that could "
                    "suggest modification, but the evidence is not conclusive."
                ),
                "low": (
                    "This image shows minimal signs of manipulation. While some minor "
                    "anomalies were detected, they fall within normal ranges for "
                    "authentic photographs."
                ),
            },
            "prompt_injection": {
                "high": (
                    "This text contains clear patterns of a prompt injection or jailbreak "
                    "attempt. It includes instructions designed to override AI safety "
                    "guidelines and manipulate system behavior."
                ),
                "medium": (
                    "This text contains some patterns that resemble prompt injection "
                    "techniques. While not all indicators are present, the text shows "
                    "some attempts to influence AI system behavior."
                ),
                "low": (
                    "This text shows minimal signs of prompt injection. A few minor "
                    "patterns were detected, but the overall risk is low."
                ),
            },
            "anomalous_behavior": {
                "high": (
                    "The login activity shows highly unusual patterns that suggest "
                    "the account may be compromised. Indicators include impossible "
                    "travel between locations, suspicious IP addresses, or rapid-fire "
                    "login attempts."
                ),
                "medium": (
                    "Some of the recent login activity appears unusual compared to "
                    "normal patterns. This could include logins from new locations "
                    "or devices that warrant further investigation."
                ),
                "low": (
                    "The login activity is mostly consistent with normal usage patterns. "
                    "A few minor anomalies were noted but do not indicate significant risk."
                ),
            },
            "ai_generated_content": {
                "high": (
                    "This text displays strong characteristics of AI-generated writing. "
                    "The sentence structure, vocabulary patterns, and stylistic consistency "
                    "closely match patterns typical of large language model output."
                ),
                "medium": (
                    "This text shows some characteristics that may indicate AI involvement "
                    "in its creation. Certain patterns in sentence structure and word choice "
                    "are consistent with machine-generated text."
                ),
                "low": (
                    "This text shows mostly human-like writing patterns. While a few "
                    "statistical indicators lean toward AI generation, the overall "
                    "evidence is inconclusive."
                ),
            },
        }

        # Determine severity tier
        if risk_score >= 60:
            tier = "high"
        elif risk_score >= 30:
            tier = "medium"
        else:
            tier = "low"

        type_explanations = threat_explanations.get(threat_type, {})
        if isinstance(type_explanations, dict):
            explanation = type_explanations.get(tier, "")
        else:
            explanation = ""

        if not explanation:
            explanation = (
                f"This input was analysed for {threat_type.replace('_', ' ')} "
                f"threats and received a risk score of {risk_score} out of 100. "
                f"{'Exercise caution and verify the source.' if risk_score >= 40 else 'The risk appears to be low.'}"
            )

        return explanation

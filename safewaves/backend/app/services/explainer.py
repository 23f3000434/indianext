"""
safewaves Explainability Service
=================================
Generates human-readable explanations from SHAP values and feature data
for any of the six threat detection modules.
"""

from __future__ import annotations

from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Human-readable descriptions for every feature across all six modules
# ---------------------------------------------------------------------------

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    # --- Phishing module ---
    "urgency_keyword_count": "Number of urgency-related keywords detected (e.g. 'urgent', 'immediately', 'verify')",
    "suspicious_phrase_count": "Number of known phishing phrases found (e.g. 'click here', 'verify your account')",
    "url_count": "Number of URLs embedded in the email body",
    "has_html": "Whether the email contains HTML markup, which can hide malicious links",
    "exclamation_count": "Number of exclamation marks, often used to create false urgency",
    "all_caps_word_ratio": "Ratio of ALL-CAPS words, a common pressure tactic in phishing",
    "spelling_error_indicators": "Number of brand typo-squatting patterns detected (e.g. 'paypa1' for 'paypal')",
    "emotional_manipulation_score": "Score measuring fear, greed, and curiosity triggers in the text",
    "link_text_mismatch": "Number of HTML links where the visible text differs from the actual URL",
    "sender_impersonation": "Number of well-known brand names found, suggesting impersonation",
    "subject_urgency": "Number of urgency keywords found in the email subject line",

    # --- URL module ---
    "url_length": "Total character length of the URL; excessively long URLs are suspicious",
    "dot_count": "Number of dots in the hostname; many dots suggest subdomain abuse",
    "hyphen_count": "Number of hyphens in the hostname, often used in phishing domains",
    "at_symbol": "Presence of an '@' symbol in the URL, used to disguise the real destination",
    "ip_address": "Whether the hostname is a raw IP address instead of a domain name",
    "has_https": "Whether the URL uses HTTPS; lack of encryption is a minor risk signal",
    "suspicious_tld": "Whether the top-level domain is commonly associated with malicious sites",
    "subdomain_count": "Number of subdomains; excessive subdomains can mask the real domain",
    "path_length": "Length of the URL path; long paths may indicate obfuscation",
    "query_length": "Length of the URL query string; long queries may carry encoded payloads",
    "fragment_length": "Length of the URL fragment; used occasionally for payload smuggling",
    "has_port": "Whether the URL specifies a non-standard port number",
    "digit_ratio": "Ratio of digits in the hostname; high ratios suggest randomly generated domains",
    "special_char_count": "Number of special characters in the hostname beyond dots and hyphens",
    "entropy": "Shannon entropy of the hostname; high entropy suggests random/generated domains",
    "is_shortened": "Whether the URL uses a known URL shortening service to hide the destination",
    "suspicious_keywords": "Number of suspicious keywords in the URL (e.g. 'login', 'verify', 'password')",
    "typosquatting_score": "Similarity score to known brand domains, detecting typo-squatting attempts",

    # --- Deepfake module ---
    "ela_mean": "Average error level analysis intensity; higher values suggest image manipulation",
    "ela_std": "Standard deviation of ELA intensity; inconsistencies indicate edited regions",
    "ela_max": "Maximum ELA intensity in the image; extreme values flag heavily modified areas",
    "noise_level": "Image noise level from Laplacian analysis; inconsistent noise suggests splicing",
    "color_histogram_uniformity": "Uniformity of colour distribution; overly uniform histograms suggest AI generation",
    "face_region_anomaly": "Difference in ELA energy between the centre and borders of the image",
    "jpeg_quality_estimate": "Estimated JPEG compression quality; low quality can indicate re-encoding",
    "edge_consistency": "Variance in edge magnitudes; inconsistent edges suggest composite images",

    # --- Prompt injection module ---
    "pattern_match_count": "Total number of injection pattern matches detected in the text",
    "instruction_override_count": "Number of attempts to override or ignore system instructions",
    "role_switch_count": "Number of attempts to make the AI assume a different role or persona",
    "system_extraction_count": "Number of attempts to extract system prompts or internal instructions",
    "delimiter_count": "Number of delimiter injection patterns found (e.g. code blocks, special tags)",
    "encoding_attempt": "Number of encoding-based attack patterns detected (base64, hex, etc.)",
    "jailbreak_count": "Number of known jailbreak patterns detected (e.g. DAN, developer mode)",
    "text_length": "Total length of the input text; longer texts have more room for hidden attacks",
    "uppercase_ratio": "Ratio of uppercase characters; unusual ratios can indicate obfuscation",
    "special_char_density": "Density of special characters; high density may signal encoding attacks",

    # --- Behavior anomaly module ---
    "unusual_hour_ratio": "Ratio of logins during unusual hours (1-5 AM), suggesting compromised credentials",
    "impossible_travel": "Detection of logins from locations impossible to reach in the time elapsed",
    "device_diversity": "Ratio of unique devices used; high diversity suggests credential sharing",
    "failed_login_ratio": "Ratio of failed login attempts; high failure rates indicate brute-force attacks",
    "tor_exit_node_ratio": "Ratio of logins from known TOR exit nodes or suspicious IP ranges",
    "rapid_fire_count": "Ratio of rapid-fire login attempts (under 60 seconds apart)",
    "new_location_ratio": "Ratio of logins from previously unseen locations",
    "ip_diversity": "Ratio of unique IP addresses used; high diversity suggests account compromise",

    # --- AI content detection module ---
    "avg_sentence_length": "Average number of words per sentence; AI text tends to be very regular",
    "sentence_length_variance": "Variance in sentence lengths; low variance is typical of AI writing",
    "vocabulary_richness": "Type-token ratio measuring vocabulary diversity",
    "punctuation_diversity": "Diversity of punctuation marks used in the text",
    "transition_word_density": "Density of transition words (e.g. 'however', 'furthermore'); AI uses more",
    "hedge_word_density": "Density of hedging language (e.g. 'perhaps', 'might'); AI hedges moderately",
    "repetition_score": "Ratio of repeated trigrams; AI tends to repeat less than humans",
    "burstiness": "Coefficient of variation in word frequency; humans are burstier than AI",
    "avg_word_length": "Average word length in characters; AI tends toward slightly longer words",
    "passive_voice_ratio": "Ratio of passive voice constructions; AI uses passive voice more often",
}


class ExplainabilityService:
    """Generate human-readable explanations from SHAP values and feature data."""

    def generate_explanation(
        self,
        features: dict,
        shap_values: dict,
        threat_type: str,
        risk_score: int,
    ) -> dict:
        """Build a structured explanation from model outputs.

        Args:
            features: Dict of feature names to their observed values.
            shap_values: Dict of feature names to their SHAP contribution values.
            threat_type: The threat category (e.g. 'phishing', 'malicious_url').
            risk_score: The overall risk score (0-100).

        Returns:
            Dict with 'summary', 'key_factors', and 'shap_data'.
        """
        # Sort features by absolute SHAP value (descending) and take top 5
        sorted_features = sorted(
            shap_values.items(),
            key=lambda item: abs(item[1]),
            reverse=True,
        )
        top_features = sorted_features[:5]

        # Build key_factors
        key_factors: List[Dict[str, Any]] = []
        for feat_name, shap_val in top_features:
            if shap_val > 0.01:
                impact = "negative"  # increases risk
            elif shap_val < -0.01:
                impact = "positive"  # decreases risk (increases safety)
            else:
                impact = "neutral"

            feat_value = features.get(feat_name, "N/A")
            description = FEATURE_DESCRIPTIONS.get(
                feat_name,
                f"Feature '{feat_name}' contributed to the analysis",
            )

            key_factors.append({
                "feature": feat_name,
                "value": str(feat_value),
                "impact": impact,
                "description": description,
            })

        # Build summary from top contributors
        summary = self._build_summary(
            key_factors, threat_type, risk_score,
        )

        # Build shap_data
        all_features = list(shap_values.keys())
        all_values = [shap_values[f] for f in all_features]

        shap_data = {
            "features": all_features,
            "values": all_values,
            "base_value": 0.5,
        }

        return {
            "summary": summary,
            "key_factors": key_factors,
            "shap_data": shap_data,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(
        key_factors: List[Dict[str, Any]],
        threat_type: str,
        risk_score: int,
    ) -> str:
        """Construct a clear text summary of why the input was flagged."""
        threat_labels = {
            "phishing": "a phishing attempt",
            "malicious_url": "a malicious URL",
            "deepfake": "a potentially manipulated or AI-generated image",
            "deepfake_video": "a potentially AI-synthesized or manipulated video",
            "deepfake_audio": "potentially AI-synthesized or cloned audio",
            "prompt_injection": "a prompt injection or jailbreak attempt",
            "anomalous_behavior": "anomalous login behavior",
            "ai_generated_content": "AI-generated content",
        }

        threat_label = threat_labels.get(threat_type, f"a {threat_type} threat")

        if risk_score >= 80:
            severity_text = "strong indicators"
        elif risk_score >= 60:
            severity_text = "significant indicators"
        elif risk_score >= 40:
            severity_text = "moderate indicators"
        elif risk_score >= 20:
            severity_text = "weak indicators"
        else:
            severity_text = "minimal indicators"

        # Collect the negative-impact (risk-increasing) factor descriptions
        risk_reasons = []
        for factor in key_factors:
            if factor["impact"] == "negative":
                risk_reasons.append(factor["description"].split(";")[0].lower())

        if risk_reasons:
            top_reasons = risk_reasons[:3]
            reasons_text = ", ".join(top_reasons)
            summary = (
                f"This input was flagged as {threat_label} with a risk score of "
                f"{risk_score}/100 ({severity_text}). The primary contributing "
                f"factors were: {reasons_text}."
            )
        else:
            summary = (
                f"This input was evaluated for {threat_label} and received a "
                f"risk score of {risk_score}/100 ({severity_text}). "
                f"No strong risk-increasing factors were identified."
            )

        return summary

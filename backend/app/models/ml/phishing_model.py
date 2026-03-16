"""
safewaves Phishing Email Detector
=================================
Heuristic-based phishing email analysis using NLP feature engineering.
Designed to run without pre-trained models or datasets. The architecture
supports hot-swapping a trained sklearn pipeline via the `_model` attribute.

Returns a standardised threat-assessment dict consumed by the API layer.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, Optional


class PhishingDetector:
    """Analyse an email for phishing indicators using feature engineering
    and weighted heuristic scoring.

    Usage:
        detector = PhishingDetector()
        result = detector.analyze(email_text="Dear customer, verify your account now!",
                                  subject="URGENT: Account Suspended")
    """

    # ------------------------------------------------------------------
    # Class-level configuration (easy to tune for demos / judging)
    # ------------------------------------------------------------------

    URGENCY_KEYWORDS: list[str] = [
        "urgent", "immediately", "verify", "suspended", "alert",
        "warning", "expire", "locked", "unauthorized", "confirm",
        "action required", "final notice", "last chance", "deadline",
        "account closed", "security alert", "compromised",
    ]

    SUSPICIOUS_PHRASES: list[str] = [
        "click here", "verify your account", "limited time", "act now",
        "update your information", "confirm your identity",
        "your account has been", "we noticed unusual", "dear customer",
        "dear user", "dear valued", "won a prize", "selected as a winner",
        "wire transfer", "social security", "tax refund",
    ]

    # Typo-squatted brand strings  (real brand -> common impersonation)
    BRAND_TYPOS: dict[str, list[str]] = {
        "paypal":    ["paypa1", "paypai", "paypaI", "pay-pal", "peypal"],
        "amazon":    ["amaz0n", "arnazon", "arnazon", "amazom"],
        "google":    ["go0gle", "googIe", "g00gle", "gooogle"],
        "microsoft": ["micros0ft", "rnicrosoft", "mircosoft"],
        "apple":     ["app1e", "appIe", "appie"],
        "netflix":   ["netf1ix", "netfIix", "nettflix"],
        "facebook":  ["faceb00k", "facebok", "facebo0k"],
        "instagram": ["1nstagram", "instagran", "lnstagram"],
        "linkedin":  ["1inkedin", "linkedln", "iinkedin"],
        "twitter":   ["tvvitter", "tw1tter", "twtter"],
    }

    EMOTIONAL_FEAR: list[str] = [
        "suspended", "locked", "unauthorized", "fraud", "hacked",
        "stolen", "breach", "compromised", "illegal", "violation",
    ]
    EMOTIONAL_GREED: list[str] = [
        "winner", "prize", "reward", "free", "bonus", "gift",
        "cash", "lottery", "million", "congratulations",
    ]
    EMOTIONAL_CURIOSITY: list[str] = [
        "secret", "exclusive", "private", "confidential", "shocking",
        "unbelievable", "you won't believe", "only you",
    ]

    # Feature weights used in the heuristic scorer
    FEATURE_WEIGHTS: dict[str, float] = {
        "urgency_keyword_count":      6.0,
        "suspicious_phrase_count":     8.0,
        "url_count":                   5.0,
        "has_html":                    4.0,
        "exclamation_count":           2.0,
        "all_caps_word_ratio":         8.0,
        "spelling_error_indicators":  12.0,
        "emotional_manipulation_score":15.0,
        "link_text_mismatch":         12.0,
        "sender_impersonation":       10.0,
        "subject_urgency":             7.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        """Initialise the detector.

        Args:
            model: An optional pre-trained sklearn-compatible model that
                   exposes `.predict_proba(X)`.  When *None* the built-in
                   heuristic scorer is used.
        """
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, email_text: str, subject: str = "") -> Dict[str, Any]:
        """Analyse *email_text* (and optional *subject*) for phishing signals.

        Returns:
            dict with keys: risk_score, is_threat, confidence, severity,
            features, shap_values.
        """
        text_lower = email_text.lower()
        subject_lower = subject.lower()

        features = self._extract_features(email_text, text_lower, subject, subject_lower)

        if self._model is not None:
            return self._predict_with_model(features)

        return self._heuristic_score(features)

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_features(
        self,
        raw_text: str,
        text_lower: str,
        subject: str,
        subject_lower: str,
    ) -> Dict[str, Any]:
        words = raw_text.split()
        total_words = max(len(words), 1)

        # --- Urgency keywords ------------------------------------------------
        urgency_keyword_count = sum(
            1 for kw in self.URGENCY_KEYWORDS if kw in text_lower
        )

        # --- Suspicious phrases -----------------------------------------------
        suspicious_phrase_count = sum(
            1 for phrase in self.SUSPICIOUS_PHRASES if phrase in text_lower
        )

        # --- URL count --------------------------------------------------------
        urls = re.findall(r'https?://[^\s<>"\']+', raw_text)
        url_count = len(urls)

        # --- HTML detection ---------------------------------------------------
        has_html = bool(re.search(r'<\s*(a|div|span|table|img|html|body|head)\b', raw_text, re.I))

        # --- Exclamation marks ------------------------------------------------
        exclamation_count = raw_text.count("!")

        # --- ALL-CAPS ratio ---------------------------------------------------
        caps_words = [w for w in words if w.isupper() and len(w) > 1]
        all_caps_word_ratio = len(caps_words) / total_words

        # --- Brand typo-squatting (spelling error indicators) -----------------
        spelling_error_indicators = 0
        for _brand, typos in self.BRAND_TYPOS.items():
            for typo in typos:
                if typo.lower() in text_lower:
                    spelling_error_indicators += 1

        # --- Emotional manipulation -------------------------------------------
        fear_count = sum(1 for w in self.EMOTIONAL_FEAR if w in text_lower)
        greed_count = sum(1 for w in self.EMOTIONAL_GREED if w in text_lower)
        curiosity_count = sum(1 for w in self.EMOTIONAL_CURIOSITY if w in text_lower)
        emotional_manipulation_score = min(
            (fear_count * 1.5 + greed_count * 1.2 + curiosity_count * 1.0) / 5.0,
            1.0,
        )

        # --- Link-text mismatch (HTML anchor href != visible text) ------------
        link_text_mismatch = 0
        if has_html:
            for m in re.finditer(
                r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                raw_text,
                re.I | re.S,
            ):
                href, anchor_text = m.group(1), m.group(2)
                anchor_clean = re.sub(r'<[^>]+>', '', anchor_text).strip()
                # If the anchor text looks like a URL but differs from href
                if re.match(r'https?://', anchor_clean):
                    if anchor_clean.split('/')[2] != href.split('/')[2]:
                        link_text_mismatch += 1

        # --- Sender impersonation (brand names in body text) ------------------
        sender_impersonation = 0
        for brand in self.BRAND_TYPOS:
            if brand in text_lower:
                sender_impersonation += 1

        # --- Subject-line urgency ---------------------------------------------
        subject_urgency = sum(
            1 for kw in self.URGENCY_KEYWORDS if kw in subject_lower
        )

        return {
            "urgency_keyword_count":       urgency_keyword_count,
            "suspicious_phrase_count":      suspicious_phrase_count,
            "url_count":                    url_count,
            "has_html":                     has_html,
            "exclamation_count":            exclamation_count,
            "all_caps_word_ratio":          round(all_caps_word_ratio, 4),
            "spelling_error_indicators":    spelling_error_indicators,
            "emotional_manipulation_score": round(emotional_manipulation_score, 4),
            "link_text_mismatch":           link_text_mismatch,
            "sender_impersonation":         sender_impersonation,
            "subject_urgency":              subject_urgency,
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _heuristic_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute a weighted risk score from extracted features."""

        raw_score = 0.0
        shap_values: Dict[str, float] = {}

        for feat_name, weight in self.FEATURE_WEIGHTS.items():
            value = features.get(feat_name, 0)
            # Normalise booleans to 0/1
            if isinstance(value, bool):
                value = int(value)
            contribution = float(value) * weight
            shap_values[feat_name] = round(contribution, 4)
            raw_score += contribution

        # Clamp to 0-100
        risk_score = max(0, min(100, raw_score))

        severity = self._severity_label(risk_score)
        confidence = self._confidence(features, risk_score)

        return {
            "risk_score":  round(risk_score, 2),
            "is_threat":   risk_score >= 40,
            "confidence":  round(confidence, 4),
            "severity":    severity,
            "features":    features,
            "shap_values": shap_values,
        }

    def _predict_with_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Use a pre-trained sklearn model to score.  Falls back to
        heuristic scoring if the model raises."""
        try:
            import numpy as np
            feature_vector = np.array(
                [float(int(v) if isinstance(v, bool) else v) for v in features.values()]
            ).reshape(1, -1)
            proba = self._model.predict_proba(feature_vector)[0]  # type: ignore[union-attr]
            risk_score = float(proba[1]) * 100
            severity = self._severity_label(risk_score)
            return {
                "risk_score":  round(risk_score, 2),
                "is_threat":   risk_score >= 40,
                "confidence":  round(float(max(proba)), 4),
                "severity":    severity,
                "features":    features,
                "shap_values": {k: 0.0 for k in features},
            }
        except Exception:
            return self._heuristic_score(features)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
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

    @staticmethod
    def _confidence(features: Dict[str, Any], risk_score: float) -> float:
        """Estimate confidence based on signal density.

        More features firing -> higher confidence in the verdict.
        """
        active_signals = sum(
            1 for v in features.values()
            if (isinstance(v, bool) and v)
            or (isinstance(v, (int, float)) and v > 0)
        )
        signal_ratio = active_signals / max(len(features), 1)
        # Confidence is higher when the score is extreme (clearly phish or clearly safe)
        extremity = abs(risk_score - 50) / 50
        return min(0.5 + 0.3 * signal_ratio + 0.2 * extremity, 1.0)

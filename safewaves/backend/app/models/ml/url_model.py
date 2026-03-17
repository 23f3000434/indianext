"""
safewaves Malicious URL Detector
================================
Feature-engineered URL threat analysis using lexical, structural, and
statistical signals.  Works entirely offline with no model files required.
Drop in a trained sklearn pipeline via the *model* constructor arg to
upgrade from heuristics to ML predictions.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs


class UrlDetector:
    """Analyse a single URL for indicators of malicious intent.

    Usage:
        detector = UrlDetector()
        result = detector.analyze("https://g00gle-login.tk/verify?user=1")
    """

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    SUSPICIOUS_TLDS: set[str] = {
        ".tk", ".ml", ".ga", ".cf", ".xyz", ".top", ".buzz",
        ".club", ".work", ".date", ".gq", ".review", ".stream",
        ".bid", ".racing", ".win", ".accountant", ".loan", ".men",
    }

    URL_SHORTENERS: set[str] = {
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
        "buff.ly", "rebrand.ly", "cutt.ly", "shorturl.at", "tiny.cc",
    }

    SUSPICIOUS_KEYWORDS: list[str] = [
        "login", "verify", "secure", "update", "bank", "account",
        "confirm", "password", "signin", "sign-in", "auth",
        "credential", "wallet", "billing", "invoice", "payment",
    ]

    # Top brands for typo-squatting distance checks
    TARGET_BRANDS: list[str] = [
        "google", "facebook", "amazon", "apple", "microsoft",
        "paypal", "netflix", "instagram", "twitter", "linkedin",
    ]

    FEATURE_WEIGHTS: dict[str, float] = {
        "url_length":           0.12,
        "dot_count":            3.0,
        "hyphen_count":         4.0,
        "at_symbol":            10.0,
        "ip_address":           15.0,
        "has_https":           -3.0,   # HTTPS lowers risk slightly
        "suspicious_tld":       18.0,
        "subdomain_count":      5.0,
        "path_length":          0.06,
        "query_length":         0.06,
        "fragment_length":      0.03,
        "has_port":             8.0,
        "digit_ratio":          25.0,
        "special_char_count":   3.0,
        "entropy":              3.0,
        "is_shortened":         12.0,
        "suspicious_keywords":  7.0,
        "typosquatting_score":  20.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, url: str) -> Dict[str, Any]:
        """Return a threat-assessment dict for the given *url*."""
        features = self._extract_features(url)

        if self._model is not None:
            return self._hybrid_score(features)

        return self._heuristic_score(features)

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_features(self, url: str) -> Dict[str, Any]:
        parsed = urlparse(url if "://" in url else f"http://{url}")
        hostname = parsed.hostname or ""
        path = parsed.path or ""
        query = parsed.query or ""
        fragment = parsed.fragment or ""

        # --- Basic lexical features -------------------------------------------
        url_length = len(url)
        dot_count = hostname.count(".")
        hyphen_count = hostname.count("-")
        at_symbol = "@" in url
        has_https = parsed.scheme.lower() == "https"

        # --- IP address as hostname -------------------------------------------
        ip_address = bool(re.match(
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname
        ))

        # --- TLD check --------------------------------------------------------
        tld = ""
        if "." in hostname:
            tld = "." + hostname.rsplit(".", 1)[-1]
        suspicious_tld = tld.lower() in self.SUSPICIOUS_TLDS

        # --- Subdomain depth --------------------------------------------------
        parts = hostname.split(".")
        subdomain_count = max(0, len(parts) - 2)

        # --- Lengths ----------------------------------------------------------
        path_length = len(path)
        query_length = len(query)
        fragment_length = len(fragment)

        # --- Port present -----------------------------------------------------
        has_port = parsed.port is not None and parsed.port not in (80, 443)

        # --- Digit ratio in domain --------------------------------------------
        digits_in_host = sum(c.isdigit() for c in hostname)
        digit_ratio = digits_in_host / max(len(hostname), 1)

        # --- Special characters (not alpha, digit, dot, hyphen) ---------------
        special_char_count = sum(
            1 for c in hostname if not (c.isalnum() or c in ".-")
        )

        # --- Shannon entropy of the domain ------------------------------------
        entropy = self._shannon_entropy(hostname)

        # --- Shortened URL ----------------------------------------------------
        is_shortened = any(
            hostname.lower().endswith(s) or hostname.lower() == s
            for s in self.URL_SHORTENERS
        )

        # --- Suspicious keywords in full URL ----------------------------------
        url_lower = url.lower()
        suspicious_keywords = sum(
            1 for kw in self.SUSPICIOUS_KEYWORDS if kw in url_lower
        )

        # --- Typo-squatting score (min normalised Levenshtein to brands) ------
        domain_name = parts[0] if parts else hostname
        typosquatting_score = self._typosquatting_score(domain_name.lower())

        return {
            "url_length":          url_length,
            "dot_count":           dot_count,
            "hyphen_count":        hyphen_count,
            "at_symbol":           at_symbol,
            "ip_address":          ip_address,
            "has_https":           has_https,
            "suspicious_tld":      suspicious_tld,
            "subdomain_count":     subdomain_count,
            "path_length":         path_length,
            "query_length":        query_length,
            "fragment_length":     fragment_length,
            "has_port":            has_port,
            "digit_ratio":         round(digit_ratio, 4),
            "special_char_count":  special_char_count,
            "entropy":             round(entropy, 4),
            "is_shortened":        is_shortened,
            "suspicious_keywords": suspicious_keywords,
            "typosquatting_score": round(typosquatting_score, 4),
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _heuristic_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        raw_score = 0.0
        shap_values: Dict[str, float] = {}

        for feat, weight in self.FEATURE_WEIGHTS.items():
            val = features.get(feat, 0)
            if isinstance(val, bool):
                val = int(val)
            contribution = float(val) * weight
            shap_values[feat] = round(contribution, 4)
            raw_score += contribution

        risk_score = max(0.0, min(100.0, raw_score))
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
        """Use a pre-trained sklearn model to score. Falls back to
        heuristic scoring if the model raises."""
        try:
            import numpy as np
            vec = np.array(
                [float(int(v) if isinstance(v, bool) else v) for v in features.values()]
            ).reshape(1, -1)
            proba = self._model.predict_proba(vec)[0]
            risk_score = float(proba[1]) * 100

            # Generate approximate SHAP values using feature weights as proxy
            shap_values = {}
            for feat_name, weight in self.FEATURE_WEIGHTS.items():
                val = features.get(feat_name, 0)
                if isinstance(val, bool):
                    val = int(val)
                shap_values[feat_name] = round(float(val) * weight * (proba[1] - 0.5) * 2, 4)

            severity = self._severity_label(risk_score)
            return {
                "risk_score":  round(risk_score, 2),
                "is_threat":   risk_score >= 40,
                "confidence":  round(float(max(proba)), 4),
                "severity":    severity,
                "features":    features,
                "shap_values": shap_values,
            }
        except Exception:
            return self._heuristic_score(features)

    def _hybrid_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Combine ML probability with heuristic score for robust detection.

        Takes the higher of the two scores so that obviously malicious URLs
        are never under-scored by a model trained on limited data.
        """
        heuristic = self._heuristic_score(features)
        ml = self._predict_with_model(features)

        if heuristic["risk_score"] > ml["risk_score"]:
            # Use heuristic score but keep ML confidence for transparency
            result = heuristic
            result["confidence"] = max(heuristic["confidence"], ml["confidence"])
        else:
            result = ml

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _shannon_entropy(text: str) -> float:
        """Compute Shannon entropy of *text* in bits."""
        if not text:
            return 0.0
        length = len(text)
        freq: Dict[str, int] = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        return -sum(
            (c / length) * math.log2(c / length) for c in freq.values()
        )

    def _typosquatting_score(self, domain: str) -> float:
        """Return a 0-1 score: 1.0 = very likely typosquatting a known brand.

        Uses normalised Levenshtein distance on the full domain name and
        also checks if any brand name appears as a close substring within
        hyphenated domain segments.
        """
        best = 0.0
        for brand in self.TARGET_BRANDS:
            if domain == brand:
                # Exact match is not typo-squatting
                continue
            # Check full domain
            dist = self._levenshtein(domain, brand)
            max_len = max(len(domain), len(brand))
            similarity = 1.0 - dist / max_len
            if similarity > 0.6:
                best = max(best, similarity)

            # Check hyphenated segments (e.g., "paypa1-security" -> check "paypa1")
            for segment in domain.split("-"):
                if segment == brand:
                    # Exact brand name embedded in domain
                    best = max(best, 0.9)
                elif len(segment) >= 3:
                    seg_dist = self._levenshtein(segment, brand)
                    seg_max = max(len(segment), len(brand))
                    seg_sim = 1.0 - seg_dist / seg_max
                    if seg_sim > 0.65:
                        best = max(best, seg_sim)

        return best

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return UrlDetector._levenshtein(s2, s1)
        if not s2:
            return len(s1)
        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

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
        active = sum(
            1 for v in features.values()
            if (isinstance(v, bool) and v)
            or (isinstance(v, (int, float)) and v > 0)
        )
        signal_ratio = active / max(len(features), 1)
        extremity = abs(risk_score - 50) / 50
        return min(0.5 + 0.3 * signal_ratio + 0.2 * extremity, 1.0)

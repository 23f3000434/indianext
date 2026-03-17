"""
safewaves Risk Scorer
======================
Centralised severity classification and confidence estimation for all
threat detection modules.
"""

from __future__ import annotations


class RiskScorer:
    """Calculate severity labels and confidence scores from risk assessments."""

    # ------------------------------------------------------------------
    # Severity classification
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_severity(risk_score: int) -> str:
        """Map a 0-100 risk score to a human-readable severity label.

        Args:
            risk_score: Integer risk score between 0 and 100 inclusive.

        Returns:
            One of 'critical', 'high', 'medium', 'low', or 'safe'.
        """
        if risk_score >= 80:
            return "critical"
        if risk_score >= 60:
            return "high"
        if risk_score >= 40:
            return "medium"
        if risk_score >= 20:
            return "low"
        return "safe"

    # ------------------------------------------------------------------
    # Confidence estimation
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_confidence(features: dict, risk_score: int) -> float:
        """Estimate the model's confidence in its classification.

        Confidence is higher when:
        - Feature values are strongly positive or strongly negative rather
          than sitting in an ambiguous middle ground.
        - The risk score is extreme (very high or very low) rather than
          hovering around the 40-60 uncertainty zone.

        Args:
            features: Dict of feature names to their observed values.
            risk_score: Integer risk score between 0 and 100 inclusive.

        Returns:
            A float between 0.0 and 1.0 representing confidence.
        """
        # --- Component 1: Score extremity ---
        # Distance from the midpoint (50), normalised to 0-1.
        # Scores near 0 or 100 get extremity ~1.0; scores near 50 get ~0.0.
        extremity = abs(risk_score - 50) / 50.0

        # --- Component 2: Feature signal strength ---
        # Measure how many features are decisively active (not near zero).
        if features:
            active_count = 0
            for val in features.values():
                if isinstance(val, bool):
                    if val:
                        active_count += 1
                elif isinstance(val, (int, float)):
                    if abs(float(val)) > 0.05:
                        active_count += 1
            signal_strength = active_count / len(features)
        else:
            signal_strength = 0.0

        # --- Component 3: Ambiguity penalty ---
        # Apply a penalty when the risk score is in the 40-60 "uncertain" zone.
        if 40 <= risk_score <= 60:
            ambiguity_penalty = 0.15 * (1.0 - abs(risk_score - 50) / 10.0)
        else:
            ambiguity_penalty = 0.0

        # Combine components
        confidence = (
            0.35                            # base confidence
            + 0.30 * extremity              # higher when score is extreme
            + 0.25 * signal_strength        # higher when features fire clearly
            - ambiguity_penalty             # lower when score is ambiguous
        )

        # Boost for very decisive scores
        if risk_score > 80 or risk_score < 20:
            confidence += 0.10

        # Clamp to [0.0, 1.0]
        return round(max(0.0, min(1.0, confidence)), 4)

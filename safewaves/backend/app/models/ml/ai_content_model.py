"""
safewaves AI-Generated Content Detector
=========================================
Statistical text analysis to estimate the probability that a piece of
writing was produced by a large language model.

The detector examines linguistic fingerprints that distinguish machine-
generated prose from human writing: sentence-length regularity, vocabulary
diversity, burstiness, hedge-word density, transition-word patterns, and
passive-voice frequency.

No model files or datasets are required.  Supply a trained sklearn pipeline
via the *model* constructor argument to upgrade from heuristics.
"""

from __future__ import annotations

import math
import re
import string
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


class AiContentDetector:
    """Estimate whether *text* was written by a human or an AI.

    Usage:
        detector = AiContentDetector()
        result = detector.analyze("It is important to note that furthermore ...")
    """

    # ------------------------------------------------------------------
    # Lexicons
    # ------------------------------------------------------------------

    TRANSITION_WORDS: list[str] = [
        "however", "furthermore", "moreover", "additionally", "consequently",
        "nevertheless", "in conclusion", "it is important", "it should be noted",
        "in addition", "on the other hand", "as a result", "in contrast",
        "therefore", "thus", "hence", "accordingly", "subsequently",
        "in summary", "to summarize", "in other words", "for instance",
        "for example", "specifically", "notably", "significantly",
    ]

    HEDGE_WORDS: list[str] = [
        "perhaps", "might", "could", "possibly", "arguably", "it seems",
        "likely", "unlikely", "may", "apparently", "presumably",
        "conceivably", "generally", "typically", "tends to", "often",
        "sometimes", "in some cases",
    ]

    # Past participle endings for passive-voice heuristic
    _PAST_PARTICIPLE_RE = re.compile(
        r'\b(was|were|been|being|is|are|get|got|gets)\s+'
        r'(\w+ed|\w+en|\w+ght|\w+wn|\w+id)\b',
        re.IGNORECASE,
    )

    # AI-typical ranges for each feature.  When a value falls inside the
    # range it contributes positively to the AI score.
    AI_TYPICAL_RANGES: dict[str, Tuple[float, float]] = {
        "avg_sentence_length":       (14.0, 22.0),   # AI tends to be 15-20
        "sentence_length_variance":  (0.0, 40.0),     # AI is more regular
        "vocabulary_richness":       (0.35, 0.65),    # AI moderate diversity
        "punctuation_diversity":     (0.3, 0.7),
        "transition_word_density":   (0.015, 1.0),    # AI uses *more* transitions
        "hedge_word_density":        (0.005, 0.04),   # AI hedges moderately
        "repetition_score":          (0.0, 0.15),     # AI repeats n-grams less
        "burstiness":                (0.0, 0.6),      # AI is less bursty
        "avg_word_length":           (4.2, 5.5),      # AI slightly longer words
        "passive_voice_ratio":       (0.04, 0.20),    # AI uses more passive
    }

    FEATURE_WEIGHTS: dict[str, float] = {
        "avg_sentence_length":      5.0,
        "sentence_length_variance": 8.0,
        "vocabulary_richness":      6.0,
        "punctuation_diversity":    4.0,
        "transition_word_density":  9.0,
        "hedge_word_density":       5.0,
        "repetition_score":         7.0,
        "burstiness":               10.0,
        "avg_word_length":          3.0,
        "passive_voice_ratio":      6.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyse *text* and return a threat-assessment dict.

        ``extra_data`` contains per-feature analysis notes indicating
        whether each metric falls in a human-typical or AI-typical range.
        """
        features = self._extract_features(text)
        analysis = self._per_feature_analysis(features)

        if self._model is not None:
            result = self._predict_with_model(features)
        else:
            result = self._heuristic_score(features)

        result["extra_data"] = {"feature_analysis": analysis}
        return result

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_features(self, text: str) -> Dict[str, Any]:
        sentences = self._split_sentences(text)
        words = self._tokenise(text)
        total_words = max(len(words), 1)
        text_lower = text.lower()

        # --- Sentence-level statistics ----------------------------------------
        sent_lengths = [len(self._tokenise(s)) for s in sentences] or [0]
        avg_sentence_length = sum(sent_lengths) / max(len(sent_lengths), 1)
        sentence_length_variance = self._variance(sent_lengths)

        # --- Vocabulary richness (type-token ratio) ---------------------------
        unique_words = set(w.lower() for w in words)
        vocabulary_richness = len(unique_words) / total_words

        # --- Punctuation diversity (unique punctuation / total punctuation) ----
        punct_chars = [c for c in text if c in string.punctuation]
        if punct_chars:
            punctuation_diversity = len(set(punct_chars)) / len(punct_chars)
        else:
            punctuation_diversity = 0.0

        # --- Transition word density ------------------------------------------
        transition_count = sum(
            1 for tw in self.TRANSITION_WORDS if tw in text_lower
        )
        transition_word_density = transition_count / total_words

        # --- Hedge word density -----------------------------------------------
        hedge_count = sum(
            1 for hw in self.HEDGE_WORDS if hw in text_lower
        )
        hedge_word_density = hedge_count / total_words

        # --- Repetition score (repeated trigrams / total trigrams) -------------
        trigrams = self._ngrams(words, 3)
        if trigrams:
            counts = Counter(trigrams)
            repeated = sum(c - 1 for c in counts.values() if c > 1)
            repetition_score = repeated / len(trigrams)
        else:
            repetition_score = 0.0

        # --- Burstiness (coefficient of variation of word frequencies) --------
        burstiness = self._burstiness(words)

        # --- Average word length ----------------------------------------------
        avg_word_length = sum(len(w) for w in words) / total_words

        # --- Passive voice ratio ----------------------------------------------
        passive_count = len(self._PAST_PARTICIPLE_RE.findall(text))
        passive_voice_ratio = passive_count / max(len(sentences), 1)

        return {
            "avg_sentence_length":      round(avg_sentence_length, 4),
            "sentence_length_variance": round(sentence_length_variance, 4),
            "vocabulary_richness":      round(vocabulary_richness, 4),
            "punctuation_diversity":    round(punctuation_diversity, 4),
            "transition_word_density":  round(transition_word_density, 6),
            "hedge_word_density":       round(hedge_word_density, 6),
            "repetition_score":         round(repetition_score, 4),
            "burstiness":               round(burstiness, 4),
            "avg_word_length":          round(avg_word_length, 4),
            "passive_voice_ratio":      round(passive_voice_ratio, 4),
        }

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _heuristic_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Score based on how many features fall in AI-typical ranges.

        Features in-range contribute *positively* to the AI-likelihood score.
        Features out-of-range contribute based on distance from the range.
        """
        raw = 0.0
        shap_values: Dict[str, float] = {}
        in_range_count = 0

        for feat, (lo, hi) in self.AI_TYPICAL_RANGES.items():
            val = float(features.get(feat, 0))
            weight = self.FEATURE_WEIGHTS.get(feat, 1.0)

            if lo <= val <= hi:
                # Fully in AI-typical range
                contribution = weight
                in_range_count += 1
            else:
                # Partially penalise -- the farther out, the less AI-like
                if val < lo:
                    distance = (lo - val) / max(abs(lo), 0.01)
                else:
                    distance = (val - hi) / max(abs(hi), 0.01)
                contribution = weight * max(0, 1.0 - distance)

            shap_values[feat] = round(contribution, 4)
            raw += contribution

        # Normalise: max possible is sum of all weights
        max_possible = sum(self.FEATURE_WEIGHTS.values())
        risk_score = (raw / max_possible) * 100 if max_possible else 0.0
        risk_score = max(0.0, min(100.0, risk_score))

        severity = self._severity_label(risk_score)
        confidence = self._confidence(in_range_count, len(self.AI_TYPICAL_RANGES), risk_score)

        return {
            "risk_score":  round(risk_score, 2),
            "is_threat":   risk_score >= 55,
            "confidence":  round(confidence, 4),
            "severity":    severity,
            "features":    features,
            "shap_values": shap_values,
        }

    def _predict_with_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        try:
            import numpy as np
            vec = np.array(list(features.values()), dtype=np.float64).reshape(1, -1)
            proba = self._model.predict_proba(vec)[0]
            risk_score = float(proba[1]) * 100
            return {
                "risk_score":  round(risk_score, 2),
                "is_threat":   risk_score >= 55,
                "confidence":  round(float(max(proba)), 4),
                "severity":    self._severity_label(risk_score),
                "features":    features,
                "shap_values": {k: 0.0 for k in features},
            }
        except Exception:
            return self._heuristic_score(features)

    # ------------------------------------------------------------------
    # Per-feature analysis (for extra_data)
    # ------------------------------------------------------------------

    def _per_feature_analysis(self, features: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        analysis: Dict[str, Dict[str, Any]] = {}
        for feat, (lo, hi) in self.AI_TYPICAL_RANGES.items():
            val = float(features.get(feat, 0))
            in_range = lo <= val <= hi
            if in_range:
                verdict = "ai_typical"
            elif val < lo:
                verdict = "human_typical"
            else:
                verdict = "human_typical"
            analysis[feat] = {
                "value":     val,
                "ai_range":  [lo, hi],
                "in_range":  in_range,
                "verdict":   verdict,
            }
        return analysis

    # ------------------------------------------------------------------
    # Text utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences using punctuation heuristics."""
        # Split on .!? followed by whitespace or end-of-string
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p for p in parts if len(p.split()) >= 2]

    @staticmethod
    def _tokenise(text: str) -> List[str]:
        """Simple whitespace + punctuation tokeniser."""
        return re.findall(r"[a-zA-Z']+", text)

    @staticmethod
    def _ngrams(words: List[str], n: int) -> List[str]:
        lower = [w.lower() for w in words]
        return [" ".join(lower[i:i+n]) for i in range(len(lower) - n + 1)]

    @staticmethod
    def _variance(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / (len(values) - 1)

    @staticmethod
    def _burstiness(words: List[str]) -> float:
        """Coefficient of variation of word-frequency distribution.

        Humans tend to be *burstier* (higher CV) because they cluster
        topic-specific words.  AI text distributes vocabulary more evenly.
        """
        if not words:
            return 0.0
        freq = Counter(w.lower() for w in words)
        counts = list(freq.values())
        if not counts:
            return 0.0
        mean = sum(counts) / len(counts)
        if mean == 0:
            return 0.0
        std = math.sqrt(sum((c - mean) ** 2 for c in counts) / len(counts))
        return std / mean

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
    def _confidence(
        in_range_count: int, total_features: int, risk_score: float,
    ) -> float:
        """Higher confidence when more features agree on the verdict."""
        agreement = in_range_count / max(total_features, 1)
        extremity = abs(risk_score - 50) / 50
        return min(0.4 + 0.35 * agreement + 0.25 * extremity, 1.0)

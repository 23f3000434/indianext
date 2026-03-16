"""
safewaves ML Detection Models
==============================
Heuristic-based threat detectors with sklearn-swappable architecture.
"""

from .phishing_model import PhishingDetector
from .url_model import UrlDetector
from .deepfake_model import DeepfakeDetector
from .prompt_model import PromptInjectionDetector
from .behavior_model import BehaviorAnomalyDetector
from .ai_content_model import AiContentDetector

__all__ = [
    "PhishingDetector",
    "UrlDetector",
    "DeepfakeDetector",
    "PromptInjectionDetector",
    "BehaviorAnomalyDetector",
    "AiContentDetector",
]

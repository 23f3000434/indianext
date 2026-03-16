"""
Prompt injection detection using pattern matching + ML scoring.
"""
import re
import numpy as np

# Pattern categories with weights
INJECTION_PATTERNS = {
    "instruction_override": {
        "weight": 0.35,
        "patterns": [
            r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
            r"disregard\s+(all\s+)?(previous|prior|above)\s+",
            r"forget\s+(everything|all|your|the\s+previous)",
            r"override\s+(your\s+)?(previous|prior|system|instructions?)",
            r"new\s+instructions?\s*:",
            r"from\s+now\s+on",
            r"you\s+must\s+now",
        ],
    },
    "role_hijack": {
        "weight": 0.30,
        "patterns": [
            r"you\s+are\s+now\s+(a|an)\s+",
            r"pretend\s+(you\s+are|to\s+be)",
            r"act\s+as\s+(if\s+you\s+are|a|an)\s+",
            r"roleplay\s+as",
            r"simulate\s+(being|a|an)\s+",
            r"you\s+are\s+(no\s+longer|not\s+a)",
            r"switch\s+to\s+(role|persona|mode)",
            r"jailbreak",
            r"\bDAN\b",
            r"developer\s+mode",
        ],
    },
    "system_manipulation": {
        "weight": 0.25,
        "patterns": [
            r"\[INST\]",
            r"<\|system\|>",
            r"<\|user\|>",
            r"###\s+(instruction|system|prompt)",
            r"system\s*:\s*(override|prompt|instructions?)",
            r"prompt\s+injection",
            r"base64\s+decode",
            r"eval\s*\(",
            r"__import__",
        ],
    },
    "data_extraction": {
        "weight": 0.20,
        "patterns": [
            r"reveal\s+(your|the|all)\s+(system|instructions?|prompt|context)",
            r"show\s+me\s+(your|the)\s+(prompt|instructions?|system)",
            r"what\s+(were|are)\s+your\s+(exact\s+)?(instructions?|system\s+prompt)",
            r"repeat\s+(your|the)\s+(instructions?|system|prompt)",
            r"print\s+(your|the)\s+(instructions?|system|context)",
            r"output\s+(your|the)\s+(full\s+)?(system\s+prompt|instructions?)",
            r"leak\s+(your|the)\s+",
        ],
    },
    "evasion_tactics": {
        "weight": 0.15,
        "patterns": [
            r"in\s+(base64|rot13|binary|hex)",
            r"translate\s+this\s+to\s+",
            r"respond\s+(in\s+)?(l33tspeak|pig\s+latin|reverse)",
            r"a[\s\-_]s[\s\-_]s[\s\-_]i[\s\-_]s[\s\-_]t",
            r"write\s+a\s+(poem|story|song)\s+about\s+(how\s+to|making|creating)",
        ],
    },
}


def analyze_prompt(text: str) -> dict:
    text_lower = text.lower()
    matched_categories = {}
    all_triggers = []
    total_score = 0.0

    for category, info in INJECTION_PATTERNS.items():
        category_matches = []
        for pattern in info["patterns"]:
            matches = re.findall(pattern, text_lower)
            if matches:
                category_matches.extend([m if isinstance(m, str) else str(m) for m in matches])

        if category_matches:
            category_score = min(info["weight"] * (1 + 0.1 * len(category_matches)), info["weight"] * 1.5)
            total_score += category_score
            matched_categories[category] = {
                "triggers": list(set(category_matches))[:5],
                "score_contribution": round(category_score, 3),
            }
            all_triggers.extend(category_matches)

    # Normalize score to 0-100
    risk_score = min(int(total_score * 200), 100)

    # Additional heuristics
    if len(text) > 2000:
        risk_score = min(risk_score + 5, 100)
    if text.count("\n") > 20:
        risk_score = min(risk_score + 5, 100)

    is_injection = risk_score >= 30

    severity = "low"
    if risk_score >= 70:
        severity = "critical"
    elif risk_score >= 50:
        severity = "high"
    elif risk_score >= 30:
        severity = "medium"

    shap_like = [
        {"feature": cat, "value": 1 if cat in matched_categories else 0, "shap": info["weight"] if cat in matched_categories else 0.0}
        for cat, info in INJECTION_PATTERNS.items()
    ]
    shap_like.sort(key=lambda x: abs(x["shap"]), reverse=True)

    return {
        "is_injection": is_injection,
        "risk_score": risk_score,
        "severity": severity,
        "confidence": min(0.5 + total_score, 0.99),
        "matched_categories": matched_categories,
        "triggers": list(set(all_triggers))[:8],
        "shap_values": shap_like,
        "text_length": len(text),
        "line_count": text.count("\n") + 1,
    }

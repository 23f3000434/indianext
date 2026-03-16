"""
Email/Text phishing detection using TF-IDF + Gradient Boosting + SHAP.
"""
import os
import re
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "email_model.joblib")

PHISHING_INDICATORS = [
    "verify your account", "update your information", "click here to confirm",
    "your account has been suspended", "unusual sign-in activity", "verify your identity",
    "your account will be closed", "you have won", "claim your prize", "limited time offer",
    "act now", "immediate response required", "urgent", "congratulations",
    "free gift", "won a lottery", "selected as a winner", "dear customer",
    "dear user", "kindly verify", "enter your password", "reset your password",
    "your bank account", "security alert", "suspicious activity", "verify now",
    "click the link below", "do not ignore", "important notice"
]

LEGITIMATE_INDICATORS = [
    "meeting agenda", "project update", "team standup", "invoice attached",
    "quarterly report", "conference call", "please find attached", "as per our discussion",
    "looking forward to", "best regards", "sincerely", "kind regards", "schedule",
    "follow up", "implementation", "deployment", "code review", "pull request"
]


def extract_email_meta_features(text: str) -> dict:
    text_lower = text.lower()
    return {
        "has_urgency": int(any(w in text_lower for w in ["urgent", "immediately", "asap", "act now", "expire"])),
        "has_threats": int(any(w in text_lower for w in ["suspended", "closed", "terminated", "blocked", "disabled"])),
        "has_money": int(any(w in text_lower for w in ["$", "prize", "reward", "gift", "lottery", "won", "cash"])),
        "has_links": len(re.findall(r"http[s]?://\S+", text)),
        "suspicious_links": int(bool(re.search(r"http[s]?://\S*(login|verify|secure|account|update)\S*", text, re.I))),
        "has_spoofed_sender": int(bool(re.search(r"(paypal|amazon|google|microsoft|apple|bank)\S*@(?!paypal|amazon|google|microsoft|apple)", text, re.I))),
        "exclamation_count": text.count("!"),
        "caps_ratio": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        "phishing_phrase_count": sum(1 for phrase in PHISHING_INDICATORS if phrase in text_lower),
        "word_count": len(text.split()),
        "avg_word_length": np.mean([len(w) for w in text.split()]) if text.split() else 0,
    }


def load_model():
    return joblib.load(MODEL_PATH)


def predict(text: str):
    import shap

    pipeline = load_model()
    proba = pipeline.predict_proba([text])[0]
    pred = int(np.argmax(proba))
    confidence = float(proba[pred])

    # SHAP with TreeExplainer on the classifier step
    clf = pipeline.named_steps["clf"]
    vectorizer = pipeline.named_steps["tfidf"]
    X_sparse = vectorizer.transform([text])
    # Convert to dense float64 for SHAP compatibility
    X_dense = np.asarray(X_sparse.todense(), dtype=np.float64)

    explainer = shap.TreeExplainer(clf)
    shap_raw = np.array(explainer.shap_values(X_dense))
    # GradientBoosting binary: (n_samples, n_features) or (1, n_samples, n_features)
    if shap_raw.ndim == 3:
        vals = shap_raw[0][0] if shap_raw.shape[0] == 1 else shap_raw[1][0]
    elif shap_raw.ndim == 2:
        vals = shap_raw[0]
    else:
        vals = shap_raw

    feature_names = vectorizer.get_feature_names_out()
    top_idxs = np.argsort(np.abs(vals))[::-1][:10]
    shap_dict = [
        {"feature": feature_names[i], "value": float(X_sparse[0, i]), "shap": float(vals[i])}
        for i in top_idxs
    ]

    meta = extract_email_meta_features(text)

    return {
        "is_phishing": bool(pred),
        "confidence": confidence,
        "risk_score": int(proba[1] * 100),
        "meta_features": meta,
        "shap_values": shap_dict,
        "top_suspicious_phrases": [p for p in PHISHING_INDICATORS if p in text.lower()][:5],
    }

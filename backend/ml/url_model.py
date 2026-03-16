"""
URL feature extraction and Random Forest model for malicious URL detection.
"""
import os
import re
import math
import joblib
import numpy as np
from urllib.parse import urlparse

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "url_model.joblib")
FEATURE_NAMES = [
    "url_length",
    "domain_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_slashes",
    "num_digits",
    "num_special_chars",
    "has_ip",
    "has_suspicious_tld",
    "subdomain_depth",
    "path_depth",
    "has_https",
    "domain_entropy",
    "has_suspicious_keywords",
    "has_port",
    "has_url_shortener",
    "query_param_count",
    "has_redirect",
    "double_slash_in_path",
]

SUSPICIOUS_TLDS = {".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".click", ".download", ".win", ".loan", ".work", ".party", ".stream"}
SUSPICIOUS_KEYWORDS = ["verify", "secure", "account", "update", "login", "signin", "password", "paypal",
                       "amazon", "bank", "ebay", "apple", "microsoft", "google", "suspended", "confirm",
                       "billing", "unusual", "activity", "identity", "alert", "prize", "winner", "click"]
URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "short.link", "rebrand.ly"}


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    return -sum((v / len(s)) * math.log2(v / len(s)) for v in freq.values())


def extract_features(url: str) -> np.ndarray:
    parsed = urlparse(url if "://" in url else "http://" + url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()
    full = url.lower()

    # subdomain depth
    domain_parts = domain.split(".")
    subdomain_depth = max(0, len(domain_parts) - 2)

    # suspicious TLD
    tld = "." + domain_parts[-1] if domain_parts else ""
    has_sus_tld = int(tld in SUSPICIOUS_TLDS)

    # suspicious keywords
    has_sus_kw = int(any(kw in full for kw in SUSPICIOUS_KEYWORDS))

    # path depth
    path_depth = len([p for p in path.split("/") if p])

    # IP address
    has_ip = int(bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$", domain)))

    # URL shortener
    base_domain = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain
    has_shortener = int(base_domain in URL_SHORTENERS)

    # query params
    qp_count = len(parsed.query.split("&")) if parsed.query else 0

    # redirect indicators
    has_redirect = int("redirect" in full or "url=" in full or "returnurl" in full or "next=" in full)

    # double slash in path
    double_slash = int("//" in path)

    features = [
        len(url),
        len(domain),
        url.count("."),
        url.count("-"),
        url.count("_"),
        url.count("/"),
        sum(c.isdigit() for c in url),
        sum(c in "@!#$%^&*~;," for c in url),
        has_ip,
        has_sus_tld,
        subdomain_depth,
        path_depth,
        int(url.startswith("https")),
        shannon_entropy(domain.replace(".", "")),
        has_sus_kw,
        int(bool(parsed.port)),
        has_shortener,
        qp_count,
        has_redirect,
        double_slash,
    ]
    return np.array(features, dtype=float)


def load_model():
    return joblib.load(MODEL_PATH)


def predict(url: str):
    from sklearn.ensemble import RandomForestClassifier
    import shap

    model = load_model()
    features = extract_features(url).reshape(1, -1)
    proba = model.predict_proba(features)[0]
    pred = int(np.argmax(proba))
    confidence = float(proba[pred])

    # SHAP explanations
    explainer = shap.TreeExplainer(model)
    shap_vals = np.array(explainer.shap_values(features))
    # SHAP v0.51+: shape (1, n_features, n_classes) or (n_classes, n_samples, n_features)
    if shap_vals.ndim == 3 and shap_vals.shape[0] == 1:
        # (1, n_features, n_classes) → class 1 values
        vals = shap_vals[0, :, 1]
    elif shap_vals.ndim == 3 and shap_vals.shape[0] == 2:
        # (n_classes, n_samples, n_features) → class 1
        vals = shap_vals[1, 0, :]
    elif shap_vals.ndim == 2 and shap_vals.shape[0] == 1:
        vals = shap_vals[0]
    else:
        vals = shap_vals.flatten()[:len(FEATURE_NAMES)]

    shap_dict = [
        {"feature": FEATURE_NAMES[i], "value": float(features[0][i]), "shap": float(vals[i])}
        for i in range(len(FEATURE_NAMES))
    ]
    shap_dict.sort(key=lambda x: abs(x["shap"]), reverse=True)

    return {
        "is_malicious": bool(pred),
        "confidence": confidence,
        "risk_score": int(proba[1] * 100),
        "features": {FEATURE_NAMES[i]: float(features[0][i]) for i in range(len(FEATURE_NAMES))},
        "shap_values": shap_dict[:10],
    }

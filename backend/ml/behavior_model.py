"""
User behavior anomaly detection using Isolation Forest + SHAP.
"""
import os
import joblib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "behavior_model.joblib")

FEATURE_NAMES = [
    "login_hour",
    "failed_attempts",
    "location_change",
    "device_change",
    "sensitive_access_count",
    "requests_per_minute",
    "session_duration_min",
    "off_hours_activity",
]

FEATURE_DESCRIPTIONS = {
    "login_hour": "Hour of login (0-23)",
    "failed_attempts": "Number of failed login attempts",
    "location_change": "New/unknown login location (0/1)",
    "device_change": "Unknown device detected (0/1)",
    "sensitive_access_count": "Accesses to sensitive resources",
    "requests_per_minute": "Requests per minute rate",
    "session_duration_min": "Session duration in minutes",
    "off_hours_activity": "Activity outside business hours (0/1)",
}


def load_model():
    return joblib.load(MODEL_PATH)


def build_feature_vector(log: dict) -> np.ndarray:
    hour = int(log.get("login_hour", 9))
    off_hours = int(hour < 7 or hour > 21)
    features = [
        hour,
        float(log.get("failed_attempts", 0)),
        float(log.get("location_change", 0)),
        float(log.get("device_change", 0)),
        float(log.get("sensitive_access_count", 0)),
        float(log.get("requests_per_minute", 5)),
        float(log.get("session_duration_min", 30)),
        off_hours,
    ]
    return np.array(features, dtype=float)


def predict(log: dict):
    import shap

    model = load_model()
    features = build_feature_vector(log).reshape(1, -1)

    # Isolation Forest: decision_function < 0 = anomaly, score_samples more negative = worse
    decision = float(model.decision_function(features)[0])
    anomaly_depth = float(model.score_samples(features)[0])

    # Heuristic risk contributions (make the demo clearly interpretable)
    f = features[0]
    heuristic = 0
    if f[1] >= 3:  failed_w = min(30, int(f[1] * 4)); heuristic += failed_w
    if f[2] == 1:  heuristic += 20  # new location
    if f[3] == 1:  heuristic += 15  # new device
    if f[4] >= 5:  heuristic += min(15, int(f[4] * 2))  # sensitive access
    if f[5] > 60:  heuristic += min(20, int((f[5] - 60) / 12))  # high req rate
    if f[7] == 1:  heuristic += 10  # off hours
    heuristic = min(heuristic, 65)

    # Model depth score (0-35, complementing heuristics)
    # decision_function: positive=normal, negative=anomaly, range ≈ [-0.5, 0.5]
    model_score = int(max(0, min(35, (-decision + 0.05) * 120)))
    risk_score = min(100, heuristic + model_score)

    is_anomaly = (risk_score >= 30) or (decision < 0)

    # SHAP via TreeExplainer — handle SHAP ≥0.46 API
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(features)
    # Normalise to a flat 1-D array of length n_features
    if isinstance(shap_vals, list):
        raw = np.array(shap_vals[0]).flatten()
    else:
        raw = np.array(shap_vals).flatten()

    shap_dict = [
        {
            "feature": FEATURE_NAMES[i],
            "description": FEATURE_DESCRIPTIONS[FEATURE_NAMES[i]],
            "value": float(features[0][i]),
            "shap": float(raw[i]),
        }
        for i in range(len(FEATURE_NAMES))
    ]
    shap_dict.sort(key=lambda x: abs(x["shap"]), reverse=True)

    severity = "normal"
    if risk_score >= 70:
        severity = "critical"
    elif risk_score >= 50:
        severity = "high"
    elif risk_score >= 30:
        severity = "suspicious"

    return {
        "is_anomaly": is_anomaly,
        "risk_score": risk_score,
        "severity": severity,
        "confidence": float(min(0.5 + abs(anomaly_depth), 0.99)),
        "anomaly_score": float(anomaly_depth),
        "shap_values": shap_dict,
        "features": {FEATURE_NAMES[i]: float(features[0][i]) for i in range(len(FEATURE_NAMES))},
    }
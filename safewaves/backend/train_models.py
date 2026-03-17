"""
SafeWaves ML Model Training Script
====================================
Generates synthetic training data based on the heuristic feature distributions
from the existing detectors, then trains sklearn pipelines (RandomForest) for
phishing email and malicious URL detection.

Models are saved to data/models/ as joblib files.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "data", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

np.random.seed(42)


# ---------------------------------------------------------------------------
# 1. Phishing Email Model
# ---------------------------------------------------------------------------

def generate_phishing_data(n_samples=2000):
    """Generate synthetic phishing/legitimate email feature vectors."""
    features = []
    labels = []

    # -- Phishing samples (label=1) --
    n_phish = n_samples // 2
    for _ in range(n_phish):
        urgency = np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.3, 0.25, 0.15])
        suspicious = np.random.choice([1, 2, 3, 4], p=[0.15, 0.3, 0.35, 0.2])
        url_count = np.random.choice([1, 2, 3, 4], p=[0.3, 0.35, 0.25, 0.1])
        has_html = float(np.random.random() < 0.6)
        exclamation = np.random.choice([1, 2, 3, 4, 5], p=[0.2, 0.25, 0.25, 0.2, 0.1])
        caps_ratio = np.random.beta(3, 7) * 0.5
        spelling = np.random.choice([0, 1, 2, 3], p=[0.3, 0.35, 0.25, 0.1])
        emotional = np.random.beta(5, 3) * 0.8 + 0.2
        link_mismatch = float(np.random.random() < 0.35)
        sender_imp = np.random.choice([0, 1, 2], p=[0.3, 0.45, 0.25])
        subject_urg = np.random.choice([1, 2, 3], p=[0.3, 0.45, 0.25])

        features.append([urgency, suspicious, url_count, has_html, exclamation,
                         round(caps_ratio, 4), spelling, round(emotional, 4),
                         link_mismatch, sender_imp, subject_urg])
        labels.append(1)

    # -- Legitimate samples (label=0) --
    n_legit = n_samples - n_phish
    for _ in range(n_legit):
        urgency = np.random.choice([0, 1, 2], p=[0.6, 0.3, 0.1])
        suspicious = np.random.choice([0, 1], p=[0.8, 0.2])
        url_count = np.random.choice([0, 1, 2], p=[0.5, 0.35, 0.15])
        has_html = float(np.random.random() < 0.3)
        exclamation = np.random.choice([0, 1], p=[0.7, 0.3])
        caps_ratio = np.random.beta(1, 12) * 0.2
        spelling = 0
        emotional = np.random.beta(1, 8) * 0.3
        link_mismatch = 0.0
        sender_imp = np.random.choice([0, 1], p=[0.85, 0.15])
        subject_urg = np.random.choice([0, 1], p=[0.8, 0.2])

        features.append([urgency, suspicious, url_count, has_html, exclamation,
                         round(caps_ratio, 4), spelling, round(emotional, 4),
                         link_mismatch, sender_imp, subject_urg])
        labels.append(0)

    columns = [
        "urgency_keyword_count", "suspicious_phrase_count", "url_count",
        "has_html", "exclamation_count", "all_caps_word_ratio",
        "spelling_error_indicators", "emotional_manipulation_score",
        "link_text_mismatch", "sender_impersonation", "subject_urgency",
    ]
    return pd.DataFrame(features, columns=columns), np.array(labels)


def train_phishing_model():
    print("=" * 60)
    print("Training Phishing Email Detection Model")
    print("=" * 60)

    X, y = generate_phishing_data(n_samples=3000)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )),
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"]))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")
    print(f"5-Fold CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Save
    model_path = os.path.join(MODEL_DIR, "phishing_model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to {model_path}")
    return pipeline


# ---------------------------------------------------------------------------
# 2. URL Threat Detection Model
# ---------------------------------------------------------------------------

def generate_url_data(n_samples=2000):
    """Generate synthetic malicious/benign URL feature vectors."""
    features = []
    labels = []

    # -- Malicious URLs (label=1) --
    n_mal = n_samples // 2
    for _ in range(n_mal):
        url_length = int(np.random.normal(85, 25))
        dot_count = np.random.choice([2, 3, 4, 5], p=[0.2, 0.3, 0.3, 0.2])
        hyphen_count = np.random.choice([1, 2, 3, 4], p=[0.3, 0.3, 0.25, 0.15])
        at_symbol = float(np.random.random() < 0.15)
        ip_address = float(np.random.random() < 0.2)
        has_https = float(np.random.random() < 0.3)
        suspicious_tld = float(np.random.random() < 0.55)
        subdomain_count = np.random.choice([1, 2, 3, 4], p=[0.25, 0.35, 0.25, 0.15])
        path_length = int(np.random.normal(30, 12))
        query_length = int(np.random.normal(25, 15))
        fragment_length = int(np.random.exponential(5))
        has_port = float(np.random.random() < 0.12)
        digit_ratio = np.random.beta(3, 5) * 0.5
        special_char = np.random.choice([0, 1, 2, 3], p=[0.3, 0.35, 0.25, 0.1])
        entropy = np.random.normal(3.8, 0.5)
        is_shortened = float(np.random.random() < 0.2)
        susp_keywords = np.random.choice([1, 2, 3, 4], p=[0.25, 0.35, 0.25, 0.15])
        typosquatting = np.random.beta(4, 3) * 0.7 + 0.1

        features.append([max(10, url_length), dot_count, hyphen_count, at_symbol,
                         ip_address, has_https, suspicious_tld, subdomain_count,
                         max(0, path_length), max(0, query_length), max(0, fragment_length),
                         has_port, round(digit_ratio, 4), special_char,
                         round(max(0, entropy), 4), is_shortened, susp_keywords,
                         round(typosquatting, 4)])
        labels.append(1)

    # -- Benign URLs (label=0) --
    n_ben = n_samples - n_mal
    for _ in range(n_ben):
        url_length = int(np.random.normal(40, 15))
        dot_count = np.random.choice([1, 2, 3], p=[0.4, 0.45, 0.15])
        hyphen_count = np.random.choice([0, 1], p=[0.7, 0.3])
        at_symbol = 0.0
        ip_address = 0.0
        has_https = float(np.random.random() < 0.85)
        suspicious_tld = 0.0
        subdomain_count = np.random.choice([0, 1, 2], p=[0.5, 0.4, 0.1])
        path_length = int(np.random.normal(15, 8))
        query_length = int(np.random.exponential(8))
        fragment_length = int(np.random.exponential(2))
        has_port = 0.0
        digit_ratio = np.random.beta(1, 15) * 0.15
        special_char = 0
        entropy = np.random.normal(3.0, 0.4)
        is_shortened = 0.0
        susp_keywords = np.random.choice([0, 1], p=[0.75, 0.25])
        typosquatting = np.random.beta(1, 10) * 0.3

        features.append([max(10, url_length), dot_count, hyphen_count, at_symbol,
                         ip_address, has_https, suspicious_tld, subdomain_count,
                         max(0, path_length), max(0, query_length), max(0, fragment_length),
                         has_port, round(digit_ratio, 4), special_char,
                         round(max(0, entropy), 4), is_shortened, susp_keywords,
                         round(typosquatting, 4)])
        labels.append(0)

    columns = [
        "url_length", "dot_count", "hyphen_count", "at_symbol",
        "ip_address", "has_https", "suspicious_tld", "subdomain_count",
        "path_length", "query_length", "fragment_length", "has_port",
        "digit_ratio", "special_char_count", "entropy", "is_shortened",
        "suspicious_keywords", "typosquatting_score",
    ]
    return pd.DataFrame(features, columns=columns), np.array(labels)


def train_url_model():
    print("\n" + "=" * 60)
    print("Training Malicious URL Detection Model")
    print("=" * 60)

    X, y = generate_url_data(n_samples=3000)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        )),
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Benign", "Malicious"]))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc")
    print(f"5-Fold CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Save
    model_path = os.path.join(MODEL_DIR, "url_model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"\nModel saved to {model_path}")
    return pipeline


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    train_phishing_model()
    train_url_model()
    print("\n" + "=" * 60)
    print("All models trained and saved to data/models/")
    print("=" * 60)

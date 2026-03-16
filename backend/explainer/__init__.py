# SaveWaves Explainer

"""
LLM-powered threat explanation using Groq (free API).
Falls back to rule-based explanations if GROQ_API_KEY is not set.
"""
import os
from typing import Optional

def get_explanation(threat_type: str, detection_result: dict) -> str:
    """Generate a natural language explanation for a detected threat."""
    # Read key at call time so per-request os.environ overrides work
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return _groq_explanation(threat_type, detection_result, api_key)
    return _rule_based_explanation(threat_type, detection_result)


def _groq_explanation(threat_type: str, result: dict, api_key: str) -> str:
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        prompt = _build_prompt(threat_type, result)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return _rule_based_explanation(threat_type, result)


def _build_prompt(threat_type: str, result: dict) -> str:
    risk = result.get("risk_score", 0)
    confidence = result.get("confidence", 0)

    if threat_type == "url":
        features = result.get("features", {})
        shap = result.get("shap_values", [])
        top_factors = [s["feature"] for s in shap[:3] if s["shap"] > 0]
        return f"""You are a cybersecurity analyst. A URL was analyzed for malicious indicators.
Risk Score: {risk}/100. Confidence: {confidence:.0%}. Is malicious: {result.get('is_malicious')}.
Top suspicious factors: {', '.join(top_factors) if top_factors else 'none'}.
Key URL features: HTTPS={int(features.get('has_https',0))}, url_length={int(features.get('url_length',0))}, suspicious_keywords={int(features.get('has_suspicious_keywords',0))}, suspicious_tld={int(features.get('has_suspicious_tld',0))}.

Write a 3-sentence plain-English explanation of why this URL is {'suspicious' if result.get('is_malicious') else 'safe'}, what the user should do, and what the main risk factors are. Be direct and clear."""

    elif threat_type == "email":
        phrases = result.get("top_suspicious_phrases", [])
        meta = result.get("meta_features", {})
        return f"""You are a cybersecurity analyst. An email/text was analyzed for phishing.
Risk Score: {risk}/100. Confidence: {confidence:.0%}. Is phishing: {result.get('is_phishing')}.
Suspicious phrases found: {phrases[:3]}.
Urgency detected: {meta.get('has_urgency')}, threats detected: {meta.get('has_threats')}, money mentions: {meta.get('has_money')}.

Write a 3-sentence plain-English explanation of why this message is {'a phishing attempt' if result.get('is_phishing') else 'likely legitimate'}, what manipulation tactics were used, and what the recipient should do."""

    elif threat_type == "prompt":
        cats = list(result.get("matched_categories", {}).keys())
        return f"""You are a cybersecurity analyst specializing in AI security. A text prompt was analyzed for prompt injection attacks.
Risk Score: {risk}/100. Is injection: {result.get('is_injection')}. Severity: {result.get('severity')}.
Attack categories detected: {cats}.
Triggers found: {result.get('triggers', [])[:3]}.

Write a 3-sentence plain-English explanation of what prompt injection technique was attempted, why it is dangerous, and how AI systems should handle this."""

    elif threat_type == "behavior":
        features = result.get("features", {})
        return f"""You are a security operations analyst. A user behavior log was analyzed for anomalies.
Risk Score: {risk}/100. Is anomaly: {result.get('is_anomaly')}. Severity: {result.get('severity')}.
Login hour: {features.get('login_hour')}, failed attempts: {features.get('failed_attempts')}, location change: {features.get('location_change')}, requests/min: {features.get('requests_per_minute', 0):.1f}.

Write a 3-sentence plain-English explanation of what behavioral signals are suspicious, what attack this might indicate (brute force, account takeover, data exfiltration?), and what the security team should do."""

    return "Threat analysis complete. Review the risk score and SHAP values for details."


def _rule_based_explanation(threat_type: str, result: dict) -> str:
    risk = result.get("risk_score", 0)

    if threat_type == "url":
        if result.get("is_malicious"):
            factors = [s["feature"].replace("_", " ") for s in result.get("shap_values", [])[:3] if s["shap"] > 0]
            return (f"This URL shows a high risk score of {risk}/100, indicating likely malicious intent. "
                    f"Key suspicious indicators include: {', '.join(factors) if factors else 'suspicious structure and keywords'}. "
                    f"Do not visit this URL. Report it to your security team and check if any credentials were already submitted.")
        return (f"This URL appears legitimate with a low risk score of {risk}/100. "
                f"It uses HTTPS, has a recognizable domain, and shows no suspicious patterns. "
                f"Still exercise caution and verify the domain matches the expected sender.")

    elif threat_type == "email":
        if result.get("is_phishing"):
            phrases = result.get("top_suspicious_phrases", [])
            return (f"This message has a phishing risk score of {risk}/100. "
                    f"It uses common social engineering tactics including: {', '.join(phrases[:2]) if phrases else 'urgency and impersonation'}. "
                    f"Do not click any links, do not provide credentials, and report this to your IT security team.")
        return (f"This message appears to be legitimate (risk score: {risk}/100). "
                f"It does not contain common phishing patterns like urgency triggers or credential requests. "
                f"Always verify the sender's email address and avoid clicking unexpected links.")

    elif threat_type == "prompt":
        if result.get("is_injection"):
            cats = list(result.get("matched_categories", {}).keys())
            return (f"A prompt injection attack was detected with risk score {risk}/100 (severity: {result.get('severity')}). "
                    f"Attack techniques identified: {', '.join(cats)}. "
                    f"This input attempts to override AI system instructions. The request should be rejected and the incident logged.")
        return (f"No prompt injection indicators detected (risk score: {risk}/100). "
                f"The input follows normal conversational patterns without instruction override attempts. "
                f"Continue monitoring for multi-turn injection attempts across the session.")

    elif threat_type == "behavior":
        if result.get("is_anomaly"):
            features = result.get("features", {})
            indicators = []
            if features.get("failed_attempts", 0) > 2:
                indicators.append(f"{int(features['failed_attempts'])} failed login attempts")
            if features.get("location_change"):
                indicators.append("login from new location")
            if features.get("requests_per_minute", 0) > 50:
                indicators.append(f"high request rate ({features['requests_per_minute']:.0f}/min)")
            return (f"Anomalous behavior detected with risk score {risk}/100 (severity: {result.get('severity')}). "
                    f"Suspicious signals: {', '.join(indicators) if indicators else 'unusual access pattern'}. "
                    f"This may indicate account takeover or brute force. Force logout, require MFA re-authentication, and investigate.")
        return (f"User behavior appears normal (risk score: {risk}/100). "
                f"Login patterns, access rates, and device/location match expected baselines. "
                f"Continue baseline profiling for improved anomaly detection.")

    return f"Threat analysis complete. Risk score: {risk}/100. Review the SHAP values for detailed factor breakdown."

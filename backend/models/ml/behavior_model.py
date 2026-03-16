"""
safewaves Behavior Anomaly Detector
=====================================
Analyses login histories for suspicious behavioural patterns such as
impossible travel, brute-force attempts, TOR usage, and device switching.

Works purely from structured login-event data -- no external datasets or
model files required.  Accepts an optional sklearn model for upgraded
scoring.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


class BehaviorAnomalyDetector:
    """Detect anomalous login behaviour from a chronological event history.

    Usage:
        detector = BehaviorAnomalyDetector()
        result = detector.analyze([
            {"timestamp": "2026-03-15T02:30:00Z", "ip": "185.220.101.1",
             "location": "Moscow", "device": "Linux/Firefox", "success": False},
            {"timestamp": "2026-03-15T02:30:05Z", "ip": "185.220.101.1",
             "location": "Moscow", "device": "Linux/Firefox", "success": False},
            ...
        ])
    """

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    # Approximate great-circle distances (km) between major cities.
    # Used for impossible-travel detection.  Only a representative subset
    # is needed for a hackathon demo.
    CITY_DISTANCES: dict[tuple[str, str], float] = {
        ("new york", "london"):       5570,
        ("new york", "tokyo"):        10850,
        ("new york", "los angeles"):  3940,
        ("new york", "moscow"):       7510,
        ("new york", "sydney"):       15990,
        ("new york", "paris"):        5830,
        ("new york", "berlin"):       6380,
        ("new york", "mumbai"):       12550,
        ("new york", "beijing"):      11000,
        ("new york", "sao paulo"):    7680,
        ("london", "tokyo"):          9560,
        ("london", "moscow"):         2500,
        ("london", "sydney"):         17000,
        ("london", "paris"):          340,
        ("london", "berlin"):         930,
        ("london", "mumbai"):         7200,
        ("london", "beijing"):        8150,
        ("london", "los angeles"):    8760,
        ("los angeles", "tokyo"):     8815,
        ("los angeles", "sydney"):    12070,
        ("los angeles", "moscow"):    9780,
        ("moscow", "tokyo"):          7480,
        ("moscow", "beijing"):        5800,
        ("moscow", "mumbai"):         4700,
        ("paris", "berlin"):          880,
        ("paris", "tokyo"):           9710,
        ("berlin", "moscow"):         1610,
        ("mumbai", "tokyo"):          6740,
        ("beijing", "tokyo"):         2100,
        ("sao paulo", "london"):      9470,
        ("sao paulo", "moscow"):      11380,
        ("sydney", "tokyo"):          7820,
    }

    # Suspicious IP ranges (first octets or prefixes common to TOR / hosting)
    SUSPICIOUS_IP_PREFIXES: list[str] = [
        "185.220.",   # TOR exit nodes
        "185.100.",
        "198.98.",
        "23.129.",
        "104.244.",
        "209.141.",
        "199.249.",
        "171.25.",
        "89.234.",
        "62.102.",
        "51.15.",     # Scaleway (cheap VPS, often abused)
        "45.153.",
    ]

    # Maximum plausible travel speed (km/h) -- commercial jets top out ~900
    MAX_TRAVEL_SPEED_KMH: float = 1000.0

    FEATURE_WEIGHTS: dict[str, float] = {
        "unusual_hour_ratio":    8.0,
        "impossible_travel":    20.0,
        "device_diversity":      6.0,
        "failed_login_ratio":   15.0,
        "tor_exit_node_ratio":  18.0,
        "rapid_fire_count":     12.0,
        "new_location_ratio":    5.0,
        "ip_diversity":          4.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, login_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse a list of login events and return threat assessment.

        Each event dict should contain:
            timestamp (ISO-8601 str), ip (str), location (str),
            device (str), success (bool).

        The returned dict includes ``extra_data.anomalous_events``.
        """
        if not login_history:
            return self._empty_result()

        events = self._parse_events(login_history)
        features, anomalous = self._extract_features(events)

        if self._model is not None:
            result = self._predict_with_model(features)
        else:
            result = self._heuristic_score(features)

        result["extra_data"] = {"anomalous_events": anomalous}
        return result

    # ------------------------------------------------------------------
    # Event parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_events(
        raw: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Normalise raw event dicts (parse timestamps, lowercase locations)."""
        parsed: List[Dict[str, Any]] = []
        for entry in raw:
            ts = entry.get("timestamp", "")
            if isinstance(ts, str):
                # Support both Z-suffix and +00:00 formats
                ts = ts.replace("Z", "+00:00")
                try:
                    dt = datetime.fromisoformat(ts)
                except ValueError:
                    dt = datetime.now(tz=timezone.utc)
            else:
                dt = datetime.now(tz=timezone.utc)

            parsed.append({
                "timestamp": dt,
                "ip":        str(entry.get("ip", "")),
                "location":  str(entry.get("location", "")).lower().strip(),
                "device":    str(entry.get("device", "")),
                "success":   bool(entry.get("success", True)),
                "_raw":      entry,
            })

        parsed.sort(key=lambda e: e["timestamp"])
        return parsed

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_features(
        self, events: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        n = len(events)
        anomalous: List[Dict[str, Any]] = []

        # --- Unusual hour (1 AM - 5 AM) --------------------------------------
        unusual_hours = 0
        for e in events:
            hour = e["timestamp"].hour
            if 1 <= hour <= 5:
                unusual_hours += 1
                anomalous.append({
                    **e["_raw"],
                    "anomaly_type": "unusual_hour",
                    "detail": f"Login at {hour}:00 local time",
                })
        unusual_hour_ratio = unusual_hours / max(n, 1)

        # --- Impossible travel ------------------------------------------------
        impossible_travel_count = 0
        for i in range(1, n):
            prev, curr = events[i - 1], events[i]
            if prev["location"] and curr["location"] and prev["location"] != curr["location"]:
                dist = self._city_distance(prev["location"], curr["location"])
                if dist is not None and dist > 0:
                    dt_hours = max(
                        (curr["timestamp"] - prev["timestamp"]).total_seconds() / 3600,
                        0.001,
                    )
                    speed = dist / dt_hours
                    if speed > self.MAX_TRAVEL_SPEED_KMH:
                        impossible_travel_count += 1
                        anomalous.append({
                            **curr["_raw"],
                            "anomaly_type": "impossible_travel",
                            "detail": (
                                f"{prev['location'].title()} -> {curr['location'].title()} "
                                f"({dist:.0f} km in {dt_hours:.2f} h = {speed:.0f} km/h)"
                            ),
                        })

        impossible_travel = min(impossible_travel_count, 5) / 5.0  # normalise

        # --- Device diversity -------------------------------------------------
        unique_devices = set(e["device"] for e in events if e["device"])
        device_diversity = min(len(unique_devices) / max(n, 1), 1.0)

        # --- Failed login ratio -----------------------------------------------
        failures = sum(1 for e in events if not e["success"])
        failed_login_ratio = failures / max(n, 1)

        # --- TOR / suspicious IP ratio ----------------------------------------
        tor_count = 0
        for e in events:
            if self._is_suspicious_ip(e["ip"]):
                tor_count += 1
                anomalous.append({
                    **e["_raw"],
                    "anomaly_type": "suspicious_ip",
                    "detail": f"IP {e['ip']} matches known suspicious prefix",
                })
        tor_exit_node_ratio = tor_count / max(n, 1)

        # --- Rapid-fire logins (< 60 s apart) ---------------------------------
        rapid_fire_count = 0
        for i in range(1, n):
            delta = (events[i]["timestamp"] - events[i - 1]["timestamp"]).total_seconds()
            if delta < 60:
                rapid_fire_count += 1
                anomalous.append({
                    **events[i]["_raw"],
                    "anomaly_type": "rapid_fire",
                    "detail": f"Login {delta:.1f}s after previous attempt",
                })
        rapid_fire_norm = min(rapid_fire_count / max(n, 1), 1.0)

        # --- New location ratio -----------------------------------------------
        seen_locations: set[str] = set()
        new_location_count = 0
        for e in events:
            loc = e["location"]
            if loc and loc not in seen_locations:
                if seen_locations:  # first location is not "new"
                    new_location_count += 1
                    anomalous.append({
                        **e["_raw"],
                        "anomaly_type": "new_location",
                        "detail": f"First login from {loc.title()}",
                    })
                seen_locations.add(loc)
        new_location_ratio = new_location_count / max(n, 1)

        # --- IP diversity -----------------------------------------------------
        unique_ips = set(e["ip"] for e in events if e["ip"])
        ip_diversity = len(unique_ips) / max(n, 1)

        features: Dict[str, Any] = {
            "unusual_hour_ratio":   round(unusual_hour_ratio, 4),
            "impossible_travel":    round(impossible_travel, 4),
            "device_diversity":     round(device_diversity, 4),
            "failed_login_ratio":   round(failed_login_ratio, 4),
            "tor_exit_node_ratio":  round(tor_exit_node_ratio, 4),
            "rapid_fire_count":     round(rapid_fire_norm, 4),
            "new_location_ratio":   round(new_location_ratio, 4),
            "ip_diversity":         round(ip_diversity, 4),
        }

        # Deduplicate anomalous events by (timestamp, anomaly_type)
        seen_keys: set[str] = set()
        deduped: List[Dict[str, Any]] = []
        for a in anomalous:
            key = f"{a.get('timestamp')}|{a.get('anomaly_type')}"
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(a)

        return features, deduped

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _heuristic_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        raw = 0.0
        shap_values: Dict[str, float] = {}

        for feat, weight in self.FEATURE_WEIGHTS.items():
            val = float(features.get(feat, 0))
            contribution = val * weight
            shap_values[feat] = round(contribution, 4)
            raw += contribution

        # Scale up -- individual ratios are 0-1, weights sum to ~88
        risk_score = max(0.0, min(100.0, raw * 100 / 30))

        severity = self._severity_label(risk_score)
        confidence = self._confidence(features, risk_score)

        return {
            "risk_score":  round(risk_score, 2),
            "is_threat":   risk_score >= 35,
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
                "is_threat":   risk_score >= 35,
                "confidence":  round(float(max(proba)), 4),
                "severity":    self._severity_label(risk_score),
                "features":    features,
                "shap_values": {k: 0.0 for k in features},
            }
        except Exception:
            return self._heuristic_score(features)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _city_distance(self, city_a: str, city_b: str) -> Optional[float]:
        """Look up pre-computed distance between two cities (case-insensitive).

        Returns None if the pair is unknown.
        """
        a, b = city_a.lower(), city_b.lower()
        return self.CITY_DISTANCES.get((a, b)) or self.CITY_DISTANCES.get((b, a))

    def _is_suspicious_ip(self, ip: str) -> bool:
        return any(ip.startswith(prefix) for prefix in self.SUSPICIOUS_IP_PREFIXES)

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "risk_score":  0.0,
            "is_threat":   False,
            "confidence":  0.5,
            "severity":    "info",
            "features":    {},
            "shap_values": {},
            "extra_data":  {"anomalous_events": []},
        }

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
            if isinstance(v, (int, float)) and v > 0
        )
        signal_ratio = active / max(len(features), 1)
        extremity = abs(risk_score - 50) / 50
        return min(0.5 + 0.3 * signal_ratio + 0.2 * extremity, 1.0)

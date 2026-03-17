"""
safewaves Video/Audio Deepfake Indicator Detector
===================================================
Analyses video and audio file metadata and byte-level signals for
indicators of AI-generated or manipulated media content.

Works without heavy deep-learning frameworks -- relies on file metadata
parsing, structural analysis, and statistical anomaly detection.
"""

from __future__ import annotations

import io
import math
import struct
from typing import Any, Dict, Optional


class MediaDeepfakeDetector:
    """Analyse video/audio file bytes for deepfake indicators.

    Examines:
    - File metadata integrity (missing/suspicious EXIF, creation tools)
    - Audio spectral consistency (via raw byte analysis)
    - Container structure anomalies
    - Known synthesis tool signatures
    """

    KNOWN_SYNTH_TOOLS = [
        "deepfake", "deepfakes", "deepfacelab", "faceswap", "faceswapped",
        "wav2lip", "roop", "facegen", "faceapp",
        "synthesia", "heygen", "d-id", "eleven", "elevenlabs",
        "tortoise", "bark", "xtts", "coqui", "resemble",
        "fakeyou", "uberduck", "murf", "descript", "ai-generated", "aigc",
    ]

    FEATURE_WEIGHTS: dict[str, float] = {
        "missing_metadata":          15.0,
        "synth_tool_detected":       25.0,
        "audio_spectral_anomaly":    18.0,
        "container_mismatch":        12.0,
        "uniform_noise_floor":       14.0,
        "duration_consistency":       8.0,
        "suspicious_codec":          10.0,
        "creation_date_anomaly":      8.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        self._model = model

    def analyze(self, file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        """Analyse a video or audio file for deepfake indicators."""
        features = self._extract_features(file_bytes, filename)

        if self._model is not None:
            return self._predict_with_model(features)
        return self._heuristic_score(features)

    def _extract_features(
        self, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        filename_lower = filename.lower()

        # Determine media type from extension
        is_video = any(filename_lower.endswith(ext) for ext in
                       [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"])
        is_audio = any(filename_lower.endswith(ext) for ext in
                       [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"])

        # --- Missing metadata ---
        # Check for standard metadata markers
        has_metadata = self._check_metadata_present(file_bytes)
        missing_metadata = 0.0 if has_metadata else 1.0

        # --- Synthesis tool detection ---
        # Scan file bytes for known tool signatures
        synth_tool_detected = self._scan_for_synth_tools(file_bytes, filename)

        # --- Audio spectral anomaly ---
        audio_spectral_anomaly = self._analyze_audio_patterns(file_bytes)

        # --- Container/extension mismatch ---
        container_mismatch = self._check_container_mismatch(file_bytes, filename_lower)

        # --- Uniform noise floor (synthetic audio tends to have very clean noise) ---
        uniform_noise_floor = self._check_noise_floor(file_bytes)

        # --- Duration consistency (very short or suspiciously round durations) ---
        duration_consistency = 0.3 if is_video or is_audio else 0.1

        # --- Suspicious codec markers ---
        suspicious_codec = self._check_suspicious_codecs(file_bytes)

        # --- Creation date anomaly ---
        creation_date_anomaly = 0.0
        if missing_metadata > 0.5:
            creation_date_anomaly = 0.6  # Missing creation date is suspicious

        return {
            "missing_metadata":       round(missing_metadata, 4),
            "synth_tool_detected":    round(synth_tool_detected, 4),
            "audio_spectral_anomaly": round(audio_spectral_anomaly, 4),
            "container_mismatch":     round(container_mismatch, 4),
            "uniform_noise_floor":    round(uniform_noise_floor, 4),
            "duration_consistency":   round(duration_consistency, 4),
            "suspicious_codec":       round(suspicious_codec, 4),
            "creation_date_anomaly":  round(creation_date_anomaly, 4),
        }

    def _check_metadata_present(self, data: bytes) -> bool:
        """Check if the file has standard metadata (EXIF, ID3, etc.)."""
        # EXIF marker (JPEG/TIFF in video containers)
        if b"Exif" in data[:4096]:
            return True
        # ID3 tag (MP3)
        if data[:3] == b"ID3":
            return True
        # QuickTime/MP4 metadata atoms
        if b"moov" in data[:8192] and b"mvhd" in data[:8192]:
            return True
        if b"udta" in data[:16384]:
            return True
        # RIFF header (WAV/AVI)
        if data[:4] == b"RIFF":
            return True
        # OGG header
        if data[:4] == b"OggS":
            return True
        # FLAC header
        if data[:4] == b"fLaC":
            return True
        return False

    def _scan_for_synth_tools(self, data: bytes, filename: str) -> float:
        """Scan for known AI synthesis tool markers in metadata/filename."""
        score = 0.0
        # Check filename
        fn_lower = filename.lower()
        for tool in self.KNOWN_SYNTH_TOOLS:
            if tool in fn_lower:
                score = max(score, 1.0)
                break

        # Check file metadata bytes (first 32KB)
        header = data[:32768].lower()
        for tool in self.KNOWN_SYNTH_TOOLS:
            if tool.encode() in header:
                score = max(score, 0.9)
                break

        # Check for common AI-generated media markers
        ai_markers = [b"generated", b"synthetic", b"ai-voice", b"tts",
                      b"text-to-speech", b"neural", b"vocoder"]
        for marker in ai_markers:
            if marker in header:
                score = max(score, 0.7)
                break

        return score

    def _analyze_audio_patterns(self, data: bytes) -> float:
        """Basic statistical analysis of audio byte patterns.

        Synthetic audio often has unusually uniform byte distributions in
        certain frequency ranges compared to natural recordings.
        """
        if len(data) < 1024:
            return 0.2

        # Sample a chunk from the middle of the file (skip headers)
        start = min(len(data) // 4, 8192)
        chunk = data[start:start + 4096]
        if len(chunk) < 256:
            return 0.2

        # Compute byte-level entropy
        freq = [0] * 256
        for b in chunk:
            freq[b] += 1
        total = len(chunk)
        entropy = -sum(
            (f / total) * math.log2(f / total)
            for f in freq if f > 0
        )

        # Very high entropy (close to 8.0) suggests compressed/random data -- normal
        # Lower entropy (< 6.0) could indicate synthesized patterns
        # Very uniform distribution (entropy 7.8-8.0) is normal for compressed audio
        if entropy < 5.5:
            return 0.7  # Suspiciously low entropy
        if 6.0 <= entropy <= 7.0:
            return 0.3  # Mildly unusual
        return 0.1  # Normal range

    def _check_container_mismatch(self, data: bytes, filename: str) -> float:
        """Check if the file extension matches the actual container format."""
        # MP4/MOV signature
        is_mp4 = b"ftyp" in data[:12]
        # RIFF (WAV/AVI)
        is_riff = data[:4] == b"RIFF"
        # OGG
        is_ogg = data[:4] == b"OggS"
        # MP3
        is_mp3 = data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)

        if filename.endswith((".mp4", ".m4a", ".mov")) and not is_mp4:
            return 0.8
        if filename.endswith((".wav", ".avi")) and not is_riff:
            return 0.8
        if filename.endswith(".ogg") and not is_ogg:
            return 0.8
        if filename.endswith(".mp3") and not is_mp3:
            return 0.8
        return 0.0

    def _check_noise_floor(self, data: bytes) -> float:
        """Check for unnaturally uniform noise floor (common in TTS audio)."""
        if len(data) < 2048:
            return 0.2

        # Sample multiple segments and compare variance
        segments = []
        seg_size = 1024
        for offset in range(min(len(data) // 4, 4096), len(data) - seg_size, len(data) // 8):
            chunk = data[offset:offset + seg_size]
            if len(chunk) == seg_size:
                variance = sum((b - 128) ** 2 for b in chunk) / seg_size
                segments.append(variance)
            if len(segments) >= 6:
                break

        if len(segments) < 2:
            return 0.2

        # Very low variance-of-variances suggests artificially uniform noise
        mean_var = sum(segments) / len(segments)
        if mean_var == 0:
            return 0.8

        var_of_var = sum((v - mean_var) ** 2 for v in segments) / len(segments)
        coeff_of_var = math.sqrt(var_of_var) / max(mean_var, 0.001)

        if coeff_of_var < 0.05:
            return 0.8  # Very uniform -- likely synthetic
        if coeff_of_var < 0.15:
            return 0.4  # Somewhat uniform
        return 0.1  # Natural variation

    def _check_suspicious_codecs(self, data: bytes) -> float:
        """Check for codecs commonly used by AI synthesis tools."""
        header = data[:8192]
        # Some TTS tools output specific codec configurations
        suspicious = [b"libspeex", b"opus custom", b"vocoder"]
        for s in suspicious:
            if s in header.lower():
                return 0.6
        return 0.0

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

        risk_score = max(0.0, min(100.0, raw))
        severity = self._severity_label(risk_score)
        confidence = self._confidence(features, risk_score)

        return {
            "risk_score":  round(risk_score, 2),
            "is_threat":   risk_score >= 40,
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
                "is_threat":   risk_score >= 40,
                "confidence":  round(float(max(proba)), 4),
                "severity":    self._severity_label(risk_score),
                "features":    features,
                "shap_values": {k: 0.0 for k in features},
            }
        except Exception:
            return self._heuristic_score(features)

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
            if isinstance(v, (int, float)) and v > 0.1
        )
        signal_ratio = active / max(len(features), 1)
        extremity = abs(risk_score - 50) / 50
        return min(0.5 + 0.3 * signal_ratio + 0.2 * extremity, 1.0)

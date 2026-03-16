"""
safewaves Deepfake Image Detector
==================================
Performs Error Level Analysis (ELA) and statistical image forensics to
detect manipulated or AI-generated images.  Runs entirely with PIL and
numpy -- no heavy deep-learning frameworks required.

When a trained sklearn classifier is supplied, it is used to score the
extracted feature vector; otherwise a calibrated heuristic scorer runs.
"""

from __future__ import annotations

import base64
import io
import math
from typing import Any, Dict, Optional

import numpy as np
from PIL import Image, ImageFilter


class DeepfakeDetector:
    """Analyse raw image bytes for signs of manipulation / deepfake origin.

    Usage:
        detector = DeepfakeDetector()
        with open("suspect.jpg", "rb") as f:
            result = detector.analyze(f.read())
    """

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    ELA_QUALITY: int = 90          # JPEG re-compression quality for ELA
    ELA_SCALE: int = 20            # Amplification factor for the ELA diff

    FEATURE_WEIGHTS: dict[str, float] = {
        "ela_mean":                    0.8,
        "ela_std":                     0.5,
        "ela_max":                     0.15,
        "noise_level":                 0.6,
        "color_histogram_uniformity":  25.0,
        "face_region_anomaly":         12.0,
        "jpeg_quality_estimate":      -0.3,   # higher quality -> less suspicious
        "edge_consistency":            15.0,
    }

    def __init__(self, model: Optional[Any] = None) -> None:
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, image_bytes: bytes) -> Dict[str, Any]:
        """Return threat-assessment dict plus a *heatmap_base64* ELA overlay."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        ela_image = self._compute_ela(img)
        ela_array = np.array(ela_image, dtype=np.float64)

        features = self._extract_features(img, ela_array)
        heatmap_b64 = self._generate_heatmap(ela_array)

        if self._model is not None:
            result = self._predict_with_model(features)
        else:
            result = self._heuristic_score(features)

        result["heatmap_base64"] = heatmap_b64
        return result

    # ------------------------------------------------------------------
    # ELA computation
    # ------------------------------------------------------------------

    def _compute_ela(self, img: Image.Image) -> Image.Image:
        """Re-save at a fixed JPEG quality and return the amplified diff."""
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=self.ELA_QUALITY)
        buf.seek(0)
        recompressed = Image.open(buf).convert("RGB")

        orig_arr = np.array(img, dtype=np.float64)
        recomp_arr = np.array(recompressed, dtype=np.float64)

        diff = np.abs(orig_arr - recomp_arr) * self.ELA_SCALE
        diff = np.clip(diff, 0, 255).astype(np.uint8)
        return Image.fromarray(diff)

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_features(
        self,
        img: Image.Image,
        ela_array: np.ndarray,
    ) -> Dict[str, Any]:
        gray = np.array(img.convert("L"), dtype=np.float64)

        # --- ELA statistics ---------------------------------------------------
        ela_flat = ela_array.mean(axis=2)  # average across RGB
        ela_mean = float(np.mean(ela_flat))
        ela_std = float(np.std(ela_flat))
        ela_max = float(np.max(ela_flat))

        # --- Noise level (std-dev of Laplacian approximation) -----------------
        laplacian = self._laplacian(gray)
        noise_level = float(np.std(laplacian))

        # --- Colour histogram uniformity (low = natural) ----------------------
        color_histogram_uniformity = self._histogram_uniformity(img)

        # --- Face-region anomaly (simplified: centre rectangle heuristic) -----
        face_region_anomaly = self._face_region_anomaly(ela_flat)

        # --- JPEG quality estimate (DCT coefficient magnitude proxy) ----------
        jpeg_quality_estimate = self._estimate_jpeg_quality(img)

        # --- Edge consistency (std-dev of Sobel magnitudes) -------------------
        edge_consistency = self._edge_consistency(gray)

        return {
            "ela_mean":                   round(ela_mean, 4),
            "ela_std":                    round(ela_std, 4),
            "ela_max":                    round(ela_max, 4),
            "noise_level":                round(noise_level, 4),
            "color_histogram_uniformity": round(color_histogram_uniformity, 4),
            "face_region_anomaly":        round(face_region_anomaly, 4),
            "jpeg_quality_estimate":      round(jpeg_quality_estimate, 4),
            "edge_consistency":           round(edge_consistency, 4),
        }

    # ------------------------------------------------------------------
    # Image processing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _laplacian(gray: np.ndarray) -> np.ndarray:
        """Compute a 3x3 Laplacian convolution (edge / noise detector)."""
        kernel = np.array([[0, 1, 0],
                           [1, -4, 1],
                           [0, 1, 0]], dtype=np.float64)
        h, w = gray.shape
        padded = np.pad(gray, 1, mode="edge")
        out = np.zeros_like(gray)
        for i in range(h):
            for j in range(w):
                out[i, j] = np.sum(padded[i:i+3, j:j+3] * kernel)
        return out

    @staticmethod
    def _histogram_uniformity(img: Image.Image) -> float:
        """Measure how uniform the colour histogram is.

        Very uniform histograms (close to 1.0) can indicate synthetic images.
        """
        hist = img.histogram()  # 768 bins (256 * 3 channels)
        total = sum(hist)
        if total == 0:
            return 0.0
        probs = [h / total for h in hist]
        max_entropy = math.log2(len(hist))
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        return entropy / max_entropy if max_entropy else 0.0

    @staticmethod
    def _face_region_anomaly(ela_flat: np.ndarray) -> float:
        """Compare ELA energy in the centre rectangle vs the border.

        A large difference suggests localised editing (e.g. face swap).
        Returns a 0-1 anomaly score.
        """
        h, w = ela_flat.shape
        cy, cx = h // 2, w // 2
        rh, rw = max(h // 4, 1), max(w // 4, 1)

        centre = ela_flat[cy - rh:cy + rh, cx - rw:cx + rw]
        border_mean = (np.sum(ela_flat) - np.sum(centre)) / max(
            ela_flat.size - centre.size, 1
        )
        centre_mean = float(np.mean(centre)) if centre.size else 0.0

        diff = abs(centre_mean - border_mean)
        # Normalise: differences above 30 are very suspicious
        return min(diff / 30.0, 1.0)

    @staticmethod
    def _estimate_jpeg_quality(img: Image.Image) -> float:
        """Rough JPEG quality estimate based on re-compression file sizes."""
        sizes = []
        for q in (50, 75, 95):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q)
            sizes.append(buf.tell())

        # The original is most similar to the quality whose size is closest
        orig_buf = io.BytesIO()
        img.save(orig_buf, format="JPEG", quality=100)
        orig_size = orig_buf.tell()

        # Weighted interpolation (very rough but fast)
        qualities = [50, 75, 95]
        diffs = [abs(s - orig_size) for s in sizes]
        min_idx = int(np.argmin(diffs))
        return float(qualities[min_idx])

    @staticmethod
    def _edge_consistency(gray: np.ndarray) -> float:
        """Measure edge-magnitude variance (inconsistent edges hint at splicing).

        Returns a 0-1 score where higher = more inconsistent.
        """
        # Sobel-X
        kx = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float64)
        ky = kx.T
        h, w = gray.shape
        padded = np.pad(gray, 1, mode="edge")
        gx = np.zeros_like(gray)
        gy = np.zeros_like(gray)
        for i in range(h):
            for j in range(w):
                region = padded[i:i+3, j:j+3]
                gx[i, j] = np.sum(region * kx)
                gy[i, j] = np.sum(region * ky)
        mag = np.sqrt(gx**2 + gy**2)
        variance = float(np.std(mag))
        # Normalise: typical natural images have variance 30-80
        return min(variance / 100.0, 1.0)

    # ------------------------------------------------------------------
    # Heatmap generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_heatmap(ela_array: np.ndarray) -> str:
        """Produce a base64-encoded PNG heatmap from the ELA diff array."""
        # Convert to single-channel intensity
        intensity = ela_array.mean(axis=2).astype(np.float64)
        # Normalise to 0-255
        max_val = intensity.max() or 1.0
        normalised = (intensity / max_val * 255).astype(np.uint8)

        # Apply a simple red-hot colour map
        h, w = normalised.shape
        heatmap = np.zeros((h, w, 3), dtype=np.uint8)
        heatmap[..., 0] = normalised                           # Red channel
        heatmap[..., 1] = np.clip(normalised.astype(int) - 80, 0, 255).astype(np.uint8)  # Green
        heatmap[..., 2] = np.clip(normalised.astype(int) - 160, 0, 255).astype(np.uint8)  # Blue

        heatmap_img = Image.fromarray(heatmap)
        buf = io.BytesIO()
        heatmap_img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("ascii")

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
    def _confidence(features: Dict[str, Any], risk_score: float) -> float:
        active = sum(
            1 for v in features.values()
            if isinstance(v, (int, float)) and v > 0
        )
        signal_ratio = active / max(len(features), 1)
        extremity = abs(risk_score - 50) / 50
        return min(0.5 + 0.3 * signal_ratio + 0.2 * extremity, 1.0)

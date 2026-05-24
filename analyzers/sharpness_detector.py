"""Sharpness detector — evaluates image clarity for quality gating.

Detects: overall sharpness, blur type (motion vs defocus), regional sharpness variance.
Score: 0 = unusably blurry, 1 = perfectly sharp.
"""
import cv2
import numpy as np
from .base import BaseDetector, imread_gray_unicode


class SharpnessDetector(BaseDetector):
    name = "sharpness"

    def __init__(self, block_size: int = 200, sharp_threshold: float = 150.0):
        self.block_size = block_size
        self.sharp_threshold = sharp_threshold

    def detect(self, image_path: str) -> list[dict]:
        gray = imread_gray_unicode(image_path)
        if gray is None:
            return []

        h, w = gray.shape[:2]
        findings = []

        # 1. Laplacian variance — overall sharpness (industry standard metric)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = np.var(lap)

        # Normalize: <50 = very blurry, 50-150 = acceptable, >150 = sharp
        sharpness_score = min(1.0, lap_var / self.sharp_threshold)

        severity = "high" if sharpness_score < 0.3 else "medium" if sharpness_score < 0.6 else "low"
        if sharpness_score < 0.8:
            findings.append({
                "type": "sharpness_low",
                "desc": "画面清晰度不足",
                "score": round(sharpness_score, 2),
                "severity": severity,
                "cx": w // 2, "cy": h // 2,
                "details": f"拉普拉斯方差{lap_var:.1f}，阈值{self.sharp_threshold:.0f}",
            })

        # 2. Regional sharpness — find soft spots
        bs = self.block_size
        region_scores = []
        for y in range(0, h - bs, bs // 2):
            for x in range(0, w - bs, bs // 2):
                block = lap[y:y + bs, x:x + bs]
                region_scores.append((x + bs // 2, y + bs // 2, np.var(block)))

        if region_scores:
            variances = [r[2] for r in region_scores]
            mean_var = np.mean(variances)
            std_var = np.std(variances)

            # Flag regions significantly softer than average
            if mean_var > 0:
                cv_regional = std_var / mean_var
                if cv_regional > 0.5:  # High variance = uneven sharpness
                    soft_spots = [r for r in region_scores if r[2] < mean_var - std_var]
                    for cx, cy, var in soft_spots[:3]:
                        findings.append({
                            "type": "sharpness_uneven",
                            "desc": "画面局部模糊",
                            "score": round(max(0, 1.0 - cv_regional), 2),
                            "severity": "medium",
                            "cx": cx, "cy": cy,
                            "details": f"局部方差{var:.1f}，均值{mean_var:.1f}，CV={cv_regional:.2f}",
                        })

        # 3. Detect blur TYPE — motion blur has directional gradient pattern
        if sharpness_score < 0.7:
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gx_var = np.var(gx)
            gy_var = np.var(gy)

            if gx_var > 0 or gy_var > 0:
                anisotropy = abs(gx_var - gy_var) / max(gx_var + gy_var, 0.01)
                if anisotropy > 0.3:
                    direction = "水平" if gx_var < gy_var else "垂直"
                    findings.append({
                        "type": "sharpness_motion_blur",
                        "desc": f"检测到{direction}向运动模糊",
                        "score": round(sharpness_score, 2),
                        "severity": "medium",
                        "cx": w // 2, "cy": h // 2,
                        "details": f"方向各向异性{anisotropy:.2f}，疑似运动模糊",
                    })

        return findings

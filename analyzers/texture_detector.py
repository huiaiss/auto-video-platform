"""Texture flaw detector — finds AI-specific texture artifacts.

Detects: unnaturally smooth regions (plastic skin), inconsistent sharpness (AI stitching).
"""
import numpy as np
from .base import BaseDetector, imread_gray_unicode


class TextureDetector(BaseDetector):
    name = "texture"

    def __init__(self, block_size: int = 120, smooth_threshold_sigma: float = 1.5):
        self.block_size = block_size
        self.smooth_threshold_sigma = smooth_threshold_sigma

    def detect(self, image_path: str) -> list[dict]:
        gray = imread_gray_unicode(image_path)
        if gray is None:
            return []

        h, w = gray.shape[:2]
        flaws = []
        bs = self.block_size

        # 1. Edge density analysis — find too-smooth regions
        import cv2
        edges = cv2.Canny(gray, 50, 150)
        densities = []
        for y in range(0, h - bs, bs // 2):
            for x in range(0, w - bs, bs // 2):
                block = edges[y:y + bs, x:x + bs]
                density = np.mean(block > 0)
                densities.append((x + bs // 2, y + bs // 2, density))

        if densities:
            mean_d = np.mean([d[2] for d in densities])
            std_d = np.std([d[2] for d in densities])
            for cx, cy, density in densities:
                if density < mean_d - self.smooth_threshold_sigma * std_d:
                    flaws.append({
                        "type": "texture_smooth",
                        "desc": "纹理过于平滑（塑料感）",
                        "score": min(1.0, (mean_d - density) / max(mean_d, 0.01)),
                        "severity": "medium",
                        "cx": cx, "cy": cy,
                        "details": f"边缘密度{density:.3f}，均值{mean_d:.3f}",
                    })
                    if len(flaws) >= 5:
                        break

        # 2. Laplacian variance — inconsistent sharpness
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap_blocks = []
        for y in range(0, h - bs, bs):
            for x in range(0, w - bs, bs):
                block = lap[y:y + bs, x:x + bs]
                lap_blocks.append((x + bs // 2, y + bs // 2, np.var(block)))

        if len(lap_blocks) > 4:
            lap_vars = [b[2] for b in lap_blocks]
            lap_mean = np.mean(lap_vars)
            lap_std = np.std(lap_vars)
            cv_lap = lap_std / max(lap_mean, 0.01)
            if cv_lap > 0.8:
                sorted_blocks = sorted(lap_blocks, key=lambda b: abs(b[2] - lap_mean), reverse=True)
                for cx, cy, var in sorted_blocks[:2]:
                    flaws.append({
                        "type": "texture_inconsistent",
                        "desc": "清晰度不一致（拼接痕迹）",
                        "score": min(1.0, cv_lap / 2),
                        "severity": "low",
                        "cx": cx, "cy": cy,
                        "details": f"局部方差{var:.1f}，变异系数{cv_lap:.2f}",
                    })

        return flaws

"""Composition detector — evaluates framing, subject placement, and horizon alignment.

Detects: off-center subject (bad for product shots), tilted horizon, dead space ratio.
Score: 0 = poorly composed, 1 = well-composed.
"""
import cv2
import numpy as np
from .base import BaseDetector, imread_gray_unicode, imread_unicode


class CompositionDetector(BaseDetector):
    name = "composition"

    def __init__(self, center_tolerance: float = 0.15, tilt_threshold: float = 1.5):
        self.center_tolerance = center_tolerance   # how far from center is acceptable (ratio of image dim)
        self.tilt_threshold = tilt_threshold       # degrees of tilt considered problematic

    def detect(self, image_path: str) -> list[dict]:
        gray = imread_gray_unicode(image_path)
        img = imread_unicode(image_path)
        if gray is None:
            return []

        h, w = gray.shape[:2]
        center_x, center_y = w / 2, h / 2
        findings = []

        # 1. Saliency map — find where the "interesting" content is
        saliency = cv2.saliency.StaticSaliencyFineGrained_create()
        success, saliency_map = saliency.computeSaliency(img) if img is not None else (False, None)

        if not success or saliency_map is None:
            # Fallback: use gradient magnitude as pseudo-saliency
            gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            saliency_map = np.sqrt(gx ** 2 + gy ** 2)
            saliency_map = saliency_map / (saliency_map.max() or 1)

        # Weighted centroid of saliency — the "visual center of mass"
        yy, xx = np.mgrid[0:h, 0:w]
        total_weight = saliency_map.sum()
        if total_weight > 0:
            com_x = (xx * saliency_map).sum() / total_weight
            com_y = (yy * saliency_map).sum() / total_weight

            # Distance from geometric center as fraction of image diagonal
            diag = np.sqrt(w ** 2 + h ** 2)
            offset = np.sqrt((com_x - center_x) ** 2 + (com_y - center_y) ** 2) / diag

            if offset > self.center_tolerance:
                direction = "偏左" if com_x < center_x - w * 0.1 else \
                            "偏右" if com_x > center_x + w * 0.1 else \
                            "偏上" if com_y < center_y - h * 0.1 else "偏下"
                findings.append({
                    "type": "composition_off_center",
                    "desc": f"视觉重心{direction}",
                    "score": round(min(1.0, offset * 3), 2),
                    "severity": "high" if offset > 0.25 else "medium",
                    "cx": int(com_x), "cy": int(com_y),
                    "details": f"重心偏离几何中心{offset*100:.0f}%，建议{'居中裁剪' if offset > 0.2 else '微调构图'}",
                })

            # 2. Rule of thirds check — is subject near a thirds intersection?
            third_x, third_y = w / 3, h / 3
            thirds_points = [
                (third_x, third_y), (2 * third_x, third_y),
                (third_x, 2 * third_y), (2 * third_x, 2 * third_y),
            ]
            min_thirds_dist = min(
                np.sqrt((com_x - tx) ** 2 + (com_y - ty) ** 2) / diag
                for tx, ty in thirds_points
            )
            if min_thirds_dist > 0.2:
                findings.append({
                    "type": "composition_not_thirds",
                    "desc": "主体不在三分线交点",
                    "score": round(min_thirds_dist, 2),
                    "severity": "low",
                    "cx": int(com_x), "cy": int(com_y),
                    "details": f"距最近三分点{min_thirds_dist*100:.0f}%对角线",
                })
        else:
            com_x, com_y = center_x, center_y

        # 3. Dead space analysis — ratio of low-texture area
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.mean(edges > 0)
        if edge_density < 0.03:
            findings.append({
                "type": "composition_empty",
                "desc": "画面过于空旷",
                "score": round(1.0 - edge_density * 10, 2),
                "severity": "medium" if edge_density < 0.02 else "low",
                "cx": w // 2, "cy": h // 2,
                "details": f"边缘密度{edge_density:.3f}，画面缺乏内容",
            })

        # 4. Horizon / tilt detection via Hough lines
        edges_full = cv2.Canny(gray, 80, 200)
        lines = cv2.HoughLines(edges_full, 1, np.pi / 180, threshold=min(w, h) // 3)
        if lines is not None:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta)
                # Near-horizontal lines (0° or 180°) and near-vertical (90°)
                if angle < 15 or angle > 165:    # horizontal-ish
                    angles.append(angle if angle < 90 else angle - 180)
                elif 75 < angle < 105:           # vertical-ish
                    angles.append(angle - 90)

            if angles:
                mean_tilt = np.mean(angles)
                if abs(mean_tilt) > self.tilt_threshold:
                    findings.append({
                        "type": "composition_tilted",
                        "desc": f"画面倾斜{abs(mean_tilt):.1f}°",
                        "score": round(min(1.0, abs(mean_tilt) / 10), 2),
                        "severity": "high" if abs(mean_tilt) > 4 else "medium",
                        "cx": w // 2, "cy": h // 2,
                        "details": f"检测到水平线倾斜{mean_tilt:.1f}°，建议旋转校正",
                    })

        return findings

"""Color & exposure detector — evaluates image lighting quality.

Detects: overexposure, underexposure, color cast (white balance issues), low contrast.
Score: 0 = severe color/exposure problem, 1 = perfect exposure and color.
"""
import cv2
import numpy as np
from .base import BaseDetector, imread_unicode


class ColorDetector(BaseDetector):
    name = "color"

    def __init__(self, overexposed_pct: float = 0.35, underexposed_pct: float = 0.25):
        self.overexposed_pct = overexposed_pct    # pixel value threshold for overexposed
        self.underexposed_pct = underexposed_pct  # pixel value threshold for underexposed

    def detect(self, image_path: str) -> list[dict]:
        img = imread_unicode(image_path)
        if img is None:
            return []

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        findings = []

        # 1. Exposure analysis via histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist / hist.sum()
        total_pixels = h * w

        # Overexposed: bright pixels (>200)
        overexposed = int(hist[201:].sum() / total_pixels * 100)
        # Underexposed: dark pixels (<30)
        underexposed = int(hist[:30].sum() / total_pixels * 100)
        # Mid-tone pixels (80-180)
        mid_tone = int(hist[80:181].sum() / total_pixels * 100)

        if overexposed > 20:
            findings.append({
                "type": "color_overexposed",
                "desc": "画面过曝",
                "score": round(min(1.0, overexposed / 50), 2),
                "severity": "high" if overexposed > 40 else "medium",
                "cx": w // 2, "cy": h // 2,
                "details": f"过曝区域占比{overexposed}%，亮部细节丢失",
            })

        if underexposed > 30:
            findings.append({
                "type": "color_underexposed",
                "desc": "画面欠曝/过暗",
                "score": round(min(1.0, underexposed / 60), 2),
                "severity": "high" if underexposed > 50 else "medium",
                "cx": w // 2, "cy": h // 2,
                "details": f"欠曝区域占比{underexposed}%，暗部细节丢失",
            })

        # 2. Contrast assessment
        p5 = np.percentile(gray, 5)
        p95 = np.percentile(gray, 95)
        contrast_range = p95 - p5
        if contrast_range < 60:
            findings.append({
                "type": "color_low_contrast",
                "desc": "画面对比度不足",
                "score": round(1.0 - contrast_range / 60, 2),
                "severity": "medium" if contrast_range < 40 else "low",
                "cx": w // 2, "cy": h // 2,
                "details": f"5%-95%亮度范围仅{contrast_range:.0f}，画面发灰",
            })

        # 3. Color cast detection (white balance issue)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h_channel = hsv[:, :, 0]
        s_channel = hsv[:, :, 1]

        # Split image into regions and check color consistency
        region_size = min(w, h) // 3
        if region_size > 50:
            cy_mid, cx_mid = h // 2, w // 2
            regions = [
                hsv[0:region_size, 0:region_size],                         # top-left
                hsv[0:region_size, w - region_size:w],                     # top-right
                hsv[h - region_size:h, 0:region_size],                     # bottom-left
                hsv[h - region_size:h, w - region_size:w],                 # bottom-right
                hsv[cy_mid - region_size//2:cy_mid + region_size//2,
                    cx_mid - region_size//2:cx_mid + region_size//2],      # center
            ]

            region_hues = []
            for r in regions:
                mask = r[:, :, 1] > 30  # Only consider pixels with some saturation
                if mask.sum() > 100:
                    region_hues.append(np.mean(r[:, :, 0][mask]))

            if len(region_hues) >= 3:
                # Check if all regions have similar color cast
                mean_hue = np.mean(region_hues)
                # In HSV, 0=red, 60=yellow, 120=green, 180=cyan, 240=blue, 300=magenta
                # Neutral (no cast) means hues are well-distributed or gray-dominant
                # Strong cast means most regions cluster around a narrow hue range
                hue_std = np.std(region_hues)
                if hue_std < 15 and np.mean(s_channel) > 40:
                    cast_color = "暖色" if mean_hue < 60 or mean_hue > 300 else \
                                 "绿色" if 60 <= mean_hue < 150 else "冷色"
                    findings.append({
                        "type": "color_cast",
                        "desc": f"画面{cast_color}偏色",
                        "score": round(min(1.0, (15 - hue_std) / 15 + 0.3), 2),
                        "severity": "medium" if hue_std < 10 else "low",
                        "cx": w // 2, "cy": h // 2,
                        "details": f"各区域色调标准差{hue_std:.1f}，疑似白平衡偏移",
                    })

        # 4. Overall color quality score (inverse of problems)
        quality_deductions = sum(f["score"] for f in findings) * 0.25
        quality_score = round(max(0.0, 1.0 - quality_deductions), 2)

        # Add a summary finding if quality is good (for highlight scoring)
        if not findings:
            findings.append({
                "type": "color_good",
                "desc": "画面曝光和色彩正常",
                "score": 0.95,
                "severity": "low",
                "cx": w // 2, "cy": h // 2,
                "details": f"中间调占比{mid_tone}%，对比度{contrast_range:.0f}",
            })

        return findings

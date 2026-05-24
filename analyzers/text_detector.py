"""Text flaw detector — finds garbled AI-generated text via OCR.

AI images often contain nonsensical text — mixed alphabets, random strokes, unreadable characters.
"""
import numpy as np
from .base import BaseDetector, imread_unicode


class TextDetector(BaseDetector):
    name = "text"

    def __init__(self, languages: list[str] = None):
        self.languages = languages or ["ch_sim", "en"]
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
        return self._reader

    def detect(self, image_path: str) -> list[dict]:
        img = imread_unicode(image_path)
        if img is None:
            return []
        h, w = img.shape[:2]

        try:
            reader = self._get_reader()
            results = reader.readtext(img)
        except Exception as e:
            return [{"type": "text_error", "desc": "OCR检测失败", "score": 0, "severity": "low", "cx": w // 2, "cy": h // 2, "details": str(e)}]

        flaws = []
        for bbox, text, confidence in results:
            if confidence < 0.4:
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                flaws.append({
                    "type": "text_garbled",
                    "desc": "文字乱码",
                    "score": round(1.0 - confidence, 2),
                    "severity": "high" if confidence < 0.2 else "medium",
                    "cx": int(np.mean(xs)),
                    "cy": int(np.mean(ys)),
                    "details": f"OCR置信度{confidence:.2f}，检测到'{text[:20]}'",
                })

        return flaws

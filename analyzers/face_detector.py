"""Face flaw detector using MediaPipe Face Mesh (478 landmarks).

Detects: facial asymmetry, eye size mismatch, mouth tilt.
"""
import math
import os
import numpy as np
from PIL import Image
from .base import BaseDetector

FACE_MODEL_PATH = r"C:\temp\mediapipe_models\face_landmarker.task"


class FaceDetector(BaseDetector):
    name = "face"

    def __init__(self, model_path: str = None):
        self.model_path = model_path or FACE_MODEL_PATH
        if not os.path.exists(self.model_path):
            self._download_model()

    def _download_model(self):
        import urllib.request
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
        urllib.request.urlretrieve(url, self.model_path)

    def _euclidean(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def detect(self, image_path: str) -> list[dict]:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        img = Image.open(image_path)
        w, h = img.size
        img_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(img.convert("RGB")))

        options = vision.FaceLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=self.model_path),
            running_mode=vision.RunningMode.IMAGE,
            num_faces=5,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
        )

        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            result = landmarker.detect(img_mp)

        flaws = []
        if not result.face_landmarks:
            return flaws

        face_center_x = w / 2

        # Symmetry check pairs: (left_idx, right_idx, description)
        symmetry_pairs = [
            (33, 263, "眼内角"),
            (133, 362, "眼外角"),
            (159, 386, "上眼睑"),
            (61, 291, "嘴角"),
            (46, 276, "眉毛中点"),
            (70, 300, "眉毛外点"),
            (93, 323, "脸颊高点"),
            (129, 358, "鼻翼"),
        ]

        for face_idx, landmarks in enumerate(result.face_landmarks):
            pts = {}
            for i, lm in enumerate(landmarks):
                pts[i] = (int(lm.x * w), int(lm.y * h), lm.z * w)

            for left_idx, right_idx, desc in symmetry_pairs:
                lp, rp = pts[left_idx], pts[right_idx]
                l_dist = abs(lp[0] - face_center_x)
                r_dist = abs(rp[0] - face_center_x)
                asymmetry = abs(l_dist - r_dist)
                y_diff = abs(lp[1] - rp[1])
                z_diff = abs(lp[2] - rp[2])

                score = (asymmetry / max(w * 0.02, 1)) * 0.4 + \
                        (y_diff / max(h * 0.015, 1)) * 0.3 + \
                        (z_diff / max(w * 0.01, 1)) * 0.3

                score = min(1.0, score)  # normalize to 0-1
                if score > 0.4:
                    flaws.append({
                        "type": "face_asymmetry",
                        "desc": f"{desc}不对称",
                        "score": round(score, 2),
                        "severity": "high" if score > 0.8 else "medium",
                        "cx": (lp[0] + rp[0]) // 2,
                        "cy": (lp[1] + rp[1]) // 2,
                        "left": lp[:2], "right": rp[:2],
                        "details": f"水平偏差{asymmetry:.0f}px, 垂直偏差{y_diff:.0f}px",
                    })

            # Eye size mismatch
            left_eye_open = self._euclidean(pts[159][:2], pts[145][:2])
            left_eye_width = self._euclidean(pts[33][:2], pts[133][:2])
            right_eye_open = self._euclidean(pts[386][:2], pts[374][:2])
            right_eye_width = self._euclidean(pts[362][:2], pts[263][:2])

            if left_eye_width > 0 and right_eye_width > 0:
                left_ratio = left_eye_open / left_eye_width
                right_ratio = right_eye_open / right_eye_width
                diff = abs(left_ratio - right_ratio) / max(left_ratio, right_ratio, 0.01)
                if diff > 0.15:
                    flaws.append({
                        "type": "face_feature",
                        "desc": "双眼大小不一致",
                        "score": round(min(1.0, diff * 2), 2),
                        "severity": "high" if diff > 0.25 else "medium",
                        "cx": int((pts[33][0] + pts[263][0]) / 2),
                        "cy": int((pts[159][1] + pts[386][1]) / 2),
                        "details": f"左眼开合比{left_ratio:.2f}, 右眼{right_ratio:.2f}",
                    })

            # Mouth tilt
            ml, mr = pts[61], pts[291]
            mouth_width = self._euclidean(ml[:2], mr[:2])
            if mouth_width > 0:
                tilt = abs(ml[1] - mr[1]) / mouth_width
                if tilt > 0.6:
                    flaws.append({
                        "type": "face_feature",
                        "desc": "嘴角歪斜",
                        "score": round(tilt, 2),
                        "severity": "medium",
                        "cx": (ml[0] + mr[0]) // 2,
                        "cy": (ml[1] + mr[1]) // 2,
                        "details": f"嘴角倾斜度{tilt:.2f}",
                    })

        return flaws

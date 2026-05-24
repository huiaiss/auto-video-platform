"""Hand flaw detector using MediaPipe Hand Landmarks.

Detects: finger count anomalies, finger proportion issues, joint angle problems.
"""
import math
import os
import numpy as np
from PIL import Image
from .base import BaseDetector

MEDIAPIPE_HAND_MODEL = r"C:\temp\mediapipe_models\hand_landmarker.task"

FINGER_MCP = {"index": 5, "middle": 9, "ring": 13, "pinky": 17}
FINGER_TIP = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
EXPECTED_RATIOS = {"index": 1.0, "middle": 1.15, "ring": 0.95, "pinky": 0.72}

LANDMARK_NAMES = {
    0: "WRIST", 4: "THUMB_TIP", 8: "INDEX_TIP", 12: "MIDDLE_TIP",
    16: "RING_TIP", 20: "PINKY_TIP",
}


class HandDetector(BaseDetector):
    name = "hand"

    def __init__(self, model_path: str = None):
        self.model_path = model_path or MEDIAPIPE_HAND_MODEL
        if not os.path.exists(self.model_path):
            self._download_model()

    def _download_model(self):
        import urllib.request
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
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

        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=self.model_path),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=8,
            min_hand_detection_confidence=0.3,
            min_hand_presence_confidence=0.3,
        )

        with vision.HandLandmarker.create_from_options(options) as landmarker:
            result = landmarker.detect(img_mp)

        flaws = []
        if not result.hand_landmarks:
            return flaws

        for hand_idx, landmarks in enumerate(result.hand_landmarks):
            pts = {}
            for i in range(min(21, len(landmarks))):
                pts[i] = (int(landmarks[i].x * w), int(landmarks[i].y * h))
            if len(pts) < 21:
                continue

            # 1. Finger adhesion detection
            tips = [pts[i] for i in [4, 8, 12, 16, 20]]
            for i in range(len(tips)):
                for j in range(i + 1, len(tips)):
                    dist = self._euclidean(tips[i], tips[j])
                    if dist < 25:
                        flaws.append({
                            "type": "hand_finger_adhesion",
                            "desc": "手指粘连或数量异常",
                            "score": 0.85,
                            "severity": "high",
                            "cx": (tips[i][0] + tips[j][0]) // 2,
                            "cy": (tips[i][1] + tips[j][1]) // 2,
                            "details": f"指尖间距仅{dist:.0f}px，疑似融合",
                            "hand_index": hand_idx,
                        })

            # 2. Finger proportion (middle/index ratio)
            lengths = {}
            for name in FINGER_MCP:
                mcp = pts[FINGER_MCP[name]]
                tip = pts[FINGER_TIP[name]]
                lengths[name] = self._euclidean(tip, mcp)

            index_len = lengths.get("index", 1)
            if index_len > 0:
                for name in ["middle"]:
                    ratio = lengths[name] / index_len
                    expected = EXPECTED_RATIOS[name]
                    deviation = abs(ratio - expected)
                    if deviation > 0.18:
                        tip = pts[FINGER_TIP[name]]
                        mcp = pts[FINGER_MCP[name]]
                        flaws.append({
                            "type": "hand_proportion",
                            "desc": "中指长度比例失调",
                            "score": min(1.0, deviation * 1.5),
                            "severity": "high" if deviation > 0.3 else "medium",
                            "cx": (tip[0] + mcp[0]) // 2,
                            "cy": (tip[1] + mcp[1]) // 2,
                            "details": f"中指/食指={ratio:.2f}，正常约{expected:.2f}",
                            "hand_index": hand_idx,
                        })

            # 3. Joint angle analysis
            if all(k in pts for k in [5, 6, 7]):
                mcp, pip, dip = pts[5], pts[6], pts[7]
                v1 = (mcp[0] - pip[0], mcp[1] - pip[1])
                v2 = (dip[0] - pip[0], dip[1] - pip[1])
                dot = v1[0] * v2[0] + v1[1] * v2[1]
                mag1, mag2 = math.hypot(*v1), math.hypot(*v2)
                if mag1 > 0 and mag2 > 0:
                    cos_a = max(-1, min(1, dot / (mag1 * mag2)))
                    angle = math.degrees(math.acos(cos_a))
                    if angle < 120 or angle > 175:
                        flaws.append({
                            "type": "hand_joint",
                            "desc": "食指关节角度异常",
                            "score": min(1.0, abs(angle - 155) / 60),
                            "severity": "medium",
                            "cx": pip[0], "cy": pip[1],
                            "details": f"PIP关节角度{angle:.0f}°，正常约150-170°",
                            "hand_index": hand_idx,
                        })

        return flaws

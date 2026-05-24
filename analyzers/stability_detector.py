"""Stability detector — evaluates video shake and sudden motion.

Works on video files. For image-only inputs, returns empty (no shake to detect).
Uses Lucas-Kanade optical flow between consecutive frames.

Score: 0 = extremely shaky/unusable, 1 = perfectly stable.
"""
import cv2
import numpy as np
from .base import BaseDetector


class StabilityDetector(BaseDetector):
    name = "stability"

    def __init__(self, sample_interval: int = 3, shake_threshold_px: float = 8.0):
        self.sample_interval = sample_interval  # analyze every Nth frame
        self.shake_threshold_px = shake_threshold_px

    def detect(self, asset_path: str) -> list[dict]:
        cap = cv2.VideoCapture(asset_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if total_frames < 2:
            cap.release()
            return []

        findings = []
        prev_gray = None
        motion_magnitudes = []
        frame_idx = 0
        sampled = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % self.sample_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_gray is not None:
                    # Sparse optical flow on feature points
                    prev_pts = cv2.goodFeaturesToTrack(
                        prev_gray, maxCorners=100, qualityLevel=0.3,
                        minDistance=10, blockSize=7
                    )

                    if prev_pts is not None:
                        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                            prev_gray, gray, prev_pts, None,
                            winSize=(15, 15), maxLevel=2,
                            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
                        )

                        if next_pts is not None and status is not None:
                            good_prev = prev_pts[status == 1]
                            good_next = next_pts[status == 1]

                            if len(good_prev) > 10:
                                displacements = np.linalg.norm(good_next - good_prev, axis=1)
                                mean_motion = np.mean(displacements)
                                max_motion = np.max(displacements)
                                motion_magnitudes.append({
                                    "frame": frame_idx,
                                    "mean": mean_motion,
                                    "max": max_motion,
                                    "cx": int(np.mean(good_prev[:, 0])),
                                    "cy": int(np.mean(good_prev[:, 1])),
                                })

                prev_gray = gray
                sampled += 1

            frame_idx += 1

        cap.release()

        if not motion_magnitudes:
            return []

        means = [m["mean"] for m in motion_magnitudes]
        maxes = [m["max"] for m in motion_magnitudes]
        avg_mean = np.mean(means)
        avg_max = np.mean(maxes)

        # Overall stability score: normalized inverse of mean motion
        # <2px = very stable, 2-8px = acceptable, >8px = shaky
        stability_score = max(0.0, 1.0 - avg_mean / (self.shake_threshold_px * 2))
        stability_score = round(stability_score, 2)

        severity = "high" if stability_score < 0.4 else "medium" if stability_score < 0.7 else "low"

        # Overall assessment
        if stability_score < 0.8:
            findings.append({
                "type": "stability_low",
                "desc": "视频画面抖动",
                "score": stability_score,
                "severity": severity,
                "cx": w // 2, "cy": h // 2,
                "details": f"平均帧间位移{avg_mean:.1f}px，最大{avg_max:.1f}px，FPS{fps:.0f}",
            })

        # Find worst shake moments
        if maxes:
            worst_idx = np.argmax(maxes)
            worst = motion_magnitudes[worst_idx]
            if worst["max"] > self.shake_threshold_px * 2:
                timestamp = worst["frame"] / fps
                findings.append({
                    "type": "stability_spike",
                    "desc": f"视频在{timestamp:.1f}s处剧烈抖动",
                    "score": round(min(1.0, worst["max"] / (self.shake_threshold_px * 4)), 2),
                    "severity": "high" if worst["max"] > self.shake_threshold_px * 3 else "medium",
                    "cx": worst["cx"], "cy": worst["cy"],
                    "details": f"帧{worst['frame']}最大位移{worst['max']:.1f}px，建议裁剪此段",
                })

        # Jitter (rapid back-and-forth)
        if len(means) > 5:
            # Compute frame-to-frame change in motion direction
            diffs = np.abs(np.diff(means))
            jitter_score = np.mean(diffs)
            if jitter_score > self.shake_threshold_px * 0.5:
                findings.append({
                    "type": "stability_jitter",
                    "desc": "画面存在高频微抖动",
                    "score": round(min(1.0, jitter_score / self.shake_threshold_px), 2),
                    "severity": "medium",
                    "cx": w // 2, "cy": h // 2,
                    "details": f"帧间抖动均值{jitter_score:.1f}px，建议使用防抖处理",
                })

        return findings

"""Base analyzer — all detectors inherit from this."""
import json
import os
import time
import numpy as np
import cv2
from PIL import Image
from abc import ABC, abstractmethod


def imread_unicode(path):
    """Load image with Unicode path support (OpenCV imread doesn't handle Chinese paths on Windows)."""
    with open(path, "rb") as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imread_gray_unicode(path):
    with open(path, "rb") as f:
        data = np.frombuffer(f.read(), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)


class BaseDetector(ABC):
    """Pluggable detector. Each detector analyzes one dimension of an image."""
    name = "base"

    @abstractmethod
    def detect(self, image_path: str) -> list[dict]:
        """Return list of flaw/feature dicts, each with: type, desc, score, severity, cx, cy, details"""
        ...


class AssetAnalyzer:
    """Runs all configured detectors on an asset set and produces a unified report."""

    def __init__(self, detectors: list[BaseDetector] = None):
        self.detectors = detectors or []

    def add_detector(self, detector: BaseDetector):
        self.detectors.append(detector)

    def scan(self, image_path: str) -> dict:
        """Run all detectors on one image."""
        findings = []
        for det in self.detectors:
            t0 = time.time()
            try:
                results = det.detect(image_path)
                elapsed = time.time() - t0
                findings.append({
                    "detector": det.name,
                    "count": len(results),
                    "elapsed_s": round(elapsed, 1),
                    "findings": results,
                })
            except Exception as e:
                findings.append({
                    "detector": det.name,
                    "count": 0,
                    "elapsed_s": round(time.time() - t0, 1),
                    "error": str(e),
                })

        # Flatten all findings, sort by score
        all_items = []
        for f in findings:
            for item in f.get("findings", []):
                item["detector"] = f["detector"]
                all_items.append(item)
        all_items.sort(key=lambda x: x.get("score", 0), reverse=True)

        return {
            "image": os.path.basename(image_path),
            "detector_results": findings,
            "top_findings": all_items[:8],
            "total_findings": len(all_items),
        }

    def scan_batch(self, image_paths: list[str]) -> list[dict]:
        return [self.scan(p) for p in image_paths]


def save_report(results: list[dict], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"), "results": results},
                  f, ensure_ascii=False, indent=2)

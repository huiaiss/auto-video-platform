"""Asset analysis layer — pluggable detectors for video production quality & flaw detection."""

from .base import AssetAnalyzer, BaseDetector, save_report, imread_unicode, imread_gray_unicode

# Enterprise quality detectors (no ML downloads needed)
from .sharpness_detector import SharpnessDetector
from .color_detector import ColorDetector
from .composition_detector import CompositionDetector
from .stability_detector import StabilityDetector

# AI flaw detectors (require pre-downloaded models)
from .face_detector import FaceDetector
from .hand_detector import HandDetector
from .texture_detector import TextureDetector
from .text_detector import TextDetector

__all__ = [
    "AssetAnalyzer", "BaseDetector", "save_report",
    "imread_unicode", "imread_gray_unicode",
    # Quality
    "SharpnessDetector", "ColorDetector",
    "CompositionDetector", "StabilityDetector",
    # Flaw
    "FaceDetector", "HandDetector",
    "TextureDetector", "TextDetector",
]

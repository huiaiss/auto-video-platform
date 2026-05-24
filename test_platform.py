"""Full platform test — all detectors on test assets."""
import sys, json, os, time
sys.stdout.reconfigure(encoding='utf-8')

from analyzers.base import AssetAnalyzer, save_report

# Phase 1: Enterprise quality detectors (fast, no ML download needed)
from analyzers.sharpness_detector import SharpnessDetector
from analyzers.color_detector import ColorDetector
from analyzers.composition_detector import CompositionDetector

# Phase 1: AI flaw detectors (need pre-downloaded models)
from analyzers.face_detector import FaceDetector
from analyzers.hand_detector import HandDetector
from analyzers.texture_detector import TextureDetector
from analyzers.text_detector import TextDetector

# ---- Config ----
assets = r"d:\抖音参考视频\ai-zhaoyaojing-ep1\assets"
images = [
    os.path.join(assets, "img1_hand_scissors.png"),
    os.path.join(assets, "img2_group_photo.png"),
]

# ---- Build analyzer ----
# Quality detectors run first (fast), flaw detectors after (slower, need models)
analyzer = AssetAnalyzer([
    SharpnessDetector(),
    ColorDetector(),
    CompositionDetector(),
    FaceDetector(),
    HandDetector(),
    TextureDetector(),
    TextDetector(),
])

# ---- Run ----
print("=" * 60)
print("AUTO VIDEO PLATFORM — Full Detector Suite Test")
print("=" * 60)
print(f"Detectors: {[d.name for d in analyzer.detectors]}")
print(f"Assets: {len(images)} images")
print()

t_start = time.time()
results = analyzer.scan_batch(images)
total_time = time.time() - t_start

# ---- Report ----
for r in results:
    print(f"\n{'─' * 60}")
    print(f"Image: {r['image']} — {r['total_findings']} total findings")
    print(f"{'─' * 60}")

    quality_findings = []
    flaw_findings = []

    for d in r["detector_results"]:
        findings = d.get("findings", [])
        if d.get("error"):
            print(f"  [{d['detector']:15s}] ERROR: {d['error']}")
            continue

        print(f"  [{d['detector']:15s}] {d['count']:2d} findings ({d['elapsed_s']:5.1f}s)", end="")
        if not findings:
            print("  ✓ 正常")
        else:
            print()
            for f in findings[:4]:
                score_bar = "█" * int(f['score'] * 10) + "░" * (10 - int(f['score'] * 10))
                print(f"    [{f['severity']:7s}] [{score_bar}] {f['desc']:24s} score={f['score']:.2f}")
                print(f"              {f['details']}")

        # Categorize
        if d['detector'] in ('sharpness', 'color', 'composition'):
            quality_findings.extend(findings)
        else:
            flaw_findings.extend(findings)

    # Top highlights
    if r["top_findings"]:
        best = r["top_findings"][0]
        print(f"\n  ★ TOP FINDING: [{best['severity']}] {best['desc']} (score={best['score']:.2f}) [{best.get('detector', '?')}]")

# ---- Save ----
report_path = os.path.join(assets, "platform_full_scan.json")
save_report(results, report_path)
print(f"\n{'=' * 60}")
print(f"Done. {len(results)} images scanned in {total_time:.0f}s.")
print(f"Report: {report_path}")

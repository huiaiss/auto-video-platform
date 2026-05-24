"""End-to-end pipeline run: product analysis → creative brief → scene → HTML.

Reads an existing pipeline test output (plan + product images + scene images),
runs the full e-commerce component pipeline, generates HyperFrames HTML,
and prints the result for browser preview.
"""

import json, os, sys, uuid, traceback, io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Paths
sys.path.insert(0, r"C:\Users\Administrator\visual-hub")
sys.path.insert(0, r"d:\auto-video-platform")
os.chdir(r"C:\Users\Administrator\visual-hub")

from config import Config

# ─── Load test data ─────────────────────────────────────────
TEST_DATA = os.path.join(Config.DATA_DIR, "pipeline_test_v8.json")
with open(TEST_DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

plan = data["plans"][0]
product_images = [p for p in data.get("image_paths", []) if os.path.exists(p)]

# Collect scene images
import glob
scene_images = []
for pattern in ["data/scenes/generated/*.png", "data/scenes/*.png"]:
    for p in sorted(glob.glob(pattern)):
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            scene_images.append(os.path.abspath(p))

print(f"Product images: {len(product_images)}")
for p in product_images:
    print(f"  {p}")
print(f"Scene images: {len(scene_images)}")
for p in scene_images[:5]:
    print(f"  {os.path.basename(p)}")
if len(scene_images) > 5:
    print(f"  ... and {len(scene_images) - 5} more")

# ─── Step 1: plan → Script ──────────────────────────────────
print("\n" + "=" * 60)
print("STEP 1: plan → Script")
from services.pipeline_bridge import plan_to_script, _VIDEO_TYPE_TO_COMPONENT_SET

script = plan_to_script(plan, industry="鞋类", script_type="with_cart")
print(f"  Title: {script.title}")
print(f"  Beats: {len(script.beats)}")
for b in script.beats:
    l2_len = len(getattr(b, 'audio_l2_text', '')) if hasattr(b, 'audio_l2_text') else 0
    print(f"    Beat {b.index}: {b.text[:40]}... ({b.duration_s:.1f}s, emotion={b.emotion}, l2={l2_len}chars)")
print(f"  Outro: {script.outro.text[:50]}...")
print(f"  Total duration: {script.total_duration_s:.1f}s")

# ─── Step 2: Asset resolution ───────────────────────────────
print("\n" + "=" * 60)
print("STEP 2: Asset Pipeline")

# Build ref_analysis from plan
from services.pipeline_bridge import _build_ref_analysis
ref_analysis = _build_ref_analysis(plan, scene_images)
print(f"  Brand style: {ref_analysis.get('brand_style', {})}")

# Run asset pipeline
from builders.asset_pipeline import AssetPipeline

output_dir = os.path.join(Config.DATA_DIR, "videos", "e2e_test_" + uuid.uuid4().hex[:6])
os.makedirs(output_dir, exist_ok=True)
assets_dir = os.path.join(output_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)

asset_pipeline = AssetPipeline(assets_dir=assets_dir)

# Gather user assets: product images + scene images
user_assets = list(product_images) + list(scene_images)
asset_plan = asset_pipeline.resolve(script, ref_analysis, user_assets)
summary = asset_pipeline.summary(asset_plan)
print(f"  Beats: {summary['total_beats']}, Local assets: {summary['local_assets']}, Need gen: {summary['generation_needed']}")

# Generate missing assets if needed
if summary['generation_needed'] > 0:
    print(f"  Generating {summary['generation_needed']} missing assets...")
    asset_plan = asset_pipeline.generate_missing(asset_plan)
    summary2 = asset_pipeline.summary(asset_plan)
    print(f"  After generation: {summary2['local_assets']} local, {summary2['generation_needed']} still needed")

# Show beat → asset mapping
for beat_idx, ap in sorted(asset_plan.items()):
    asset = ap.matched_asset
    path = asset.file_path if asset else "NONE"
    asset_type = asset.asset_type if asset else "NONE"
    print(f"  Beat {beat_idx}: {asset_type} ← {os.path.basename(str(path)) if path and path != 'NONE' else path}")

# ─── Step 3: Assembly (ecommerce component set) ─────────────
print("\n" + "=" * 60)
print("STEP 3: AssemblyEngine (ecommerce)")

from builders.assembly_engine import AssemblyEngine
from services.pipeline_bridge import _PLATFORM_DIMENSIONS

component_set = _VIDEO_TYPE_TO_COMPONENT_SET.get("product_promo", "ecommerce")
print(f"  video_type='product_promo' → component_set='{component_set}'")

# Get platform dimensions
width, height = _PLATFORM_DIMENSIONS.get("douyin", _PLATFORM_DIMENSIONS["default"])

assembler = AssemblyEngine(
    output_dir=output_dir,
    tts_voice="zh-CN-YunxiNeural",
    tts_speed=1.15,
    canvas_width=width,
    canvas_height=height,
    component_set=component_set,
)

print(f"  Canvas: {width}x{height}")
print(f"  Registry size: {len(assembler._component_registry)} components")
print(f"  Registry keys: {sorted(assembler._component_registry.keys())}")

# Check component picks for each beat
print("  Component picks:")
for beat in script.beats:
    comp = assembler._pick_component(beat, None)
    in_reg = comp in assembler._component_registry
    print(f"    Beat {beat.index} ({beat.emotion}/{beat.animation}): {comp} {'✓' if in_reg else '✗ NOT IN REGISTRY!'}")

# Build storyboard (no TTS, skip audio)
print("\n  Building storyboard...")
storyboard = assembler._build_storyboard(script, asset_plan, "", "", ref_analysis)
print(f"  Storyboard scenes: {len(storyboard['scenes'])}")
for i, scene in enumerate(storyboard['scenes']):
    comp = scene['component']
    dur = scene['duration']
    cfg = scene.get('config', {})
    img = os.path.basename(str(cfg.get('img_src', ''))) or 'NONE'
    print(f"    Scene {i}: {comp} ({dur:.1f}s) img={img}")

# ─── Step 4: Generate HTML ──────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4: Generate HyperFrames HTML")

from builders.composition_builder import CompositionBuilder, StoryboardConfig

# Convert storyboard dict to StoryboardConfig
sb_config = StoryboardConfig(
    scenes=storyboard['scenes'],
    audio_src=storyboard.get('audio_src', ''),
    bgm_src=storyboard.get('bgm_src', ''),
    global_overlays=storyboard.get('global_overlays', {}),
    metadata=storyboard.get('metadata', {}),
    style=storyboard.get('style', {}),
)

# Build with ecommerce registry
builder = CompositionBuilder(component_registry=assembler._component_registry)
html = builder.build(sb_config)

html_path = os.path.join(output_dir, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# Stats
html_lines = html.count('\n')
html_size_kb = len(html.encode('utf-8')) / 1024
print(f"  Output: {html_path}")
print(f"  Size: {html_size_kb:.1f} KB, {html_lines} lines")

# Quick validation
checks = {
    "DOCTYPE": "<!doctype html>" in html.lower(),
    "GSAP CDN": "cdnjs.cloudflare.com/ajax/libs/gsap" in html,
    "Brand primary CSS": "--brand-primary" in html,
    "Brand accent CSS": "--brand-accent" in html,
    "Hook reveal component": "hrBg" in html or "hook-reveal" in html,
    "CTA outro component": "ctaBrand" in html or "ctaRing" in html,
    "Scan overlay": "scanOverlay" in html,
    "Progress bar": "progressFill" in html,
    "GSAP timeline": "gsap.timeline" in html,
    "Audio element": "narration" in html or "<audio" in html,
    "Scene visibility": "scene_0" in html,
    "No AI components leaked": all(
        ai_comp not in html
        for ai_comp in ["social-frame", "glitch-transition", "zoom-analyze", "compare-split"]
    ),
    "Ecommerce components present": any(
        ec_comp in html
        for ec_comp in ["hook-reveal", "feature-highlight", "scene-lifestyle",
                        "before-after", "trust-signal", "cta-outro"]
    ),
}

print("\n  HTML Validation:")
all_ok = True
for label, ok in checks.items():
    print(f"    {'✓' if ok else '✗'} {label}")
    if not ok:
        all_ok = False

# ─── Step 5: Summary ────────────────────────────────────────
print("\n" + "=" * 60)
print("END-TO-END PIPELINE COMPLETE")
print(f"  Output directory: {output_dir}")
print(f"  HTML file: {html_path}")
print(f"  Total duration: {sb_config.total_duration():.1f}s")
print(f"  All validation checks: {'PASSED' if all_ok else 'SOME FAILED'}")

# Write metadata
metadata = {
    "title": script.title,
    "beats": len(script.beats),
    "total_duration_s": script.total_duration_s,
    "component_set": component_set,
    "canvas": f"{width}x{height}",
    "html_path": html_path,
    "output_dir": output_dir,
    "validation": {k: v for k, v in checks.items()},
}
meta_path = os.path.join(output_dir, "metadata.json")
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\n  Metadata: {meta_path}")
print("\n  Ready for browser preview. Run:")
print(f"    start {html_path}")

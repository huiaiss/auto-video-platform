"""Benchmark: Full C1→C2 end-to-end pipeline with real timing.

C1: Product photos → Analysis → Creative Brief → Scenes → Compositing → 多平台出图
C2: Script → Asset Matching → Storyboard → HTML → 验证

Usage:
    python tests/benchmark_e2e.py
"""

import time, json, os, sys, io, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\Administrator\visual-hub")
sys.path.insert(0, r"d:\auto-video-platform")
os.chdir(r"C:\Users\Administrator\visual-hub")

from config import Config

timings = {}
total_start = time.time()

# ── PHASE 1: Load Data ──────────────────────────────────────
t1 = time.time()
TEST_DATA = os.path.join(Config.DATA_DIR, "pipeline_test_v8.json")
with open(TEST_DATA, "r", encoding="utf-8") as f:
    data = json.load(f)
plan = data["plans"][0]
product_images = [p for p in data.get("image_paths", []) if os.path.exists(p)]

# Load existing scene images (from previous scene_generator runs)
scene_images = []
for pattern in ["data/scenes/generated/*.png", "data/scenes/*.png", "data/scenes/custom/*.png"]:
    for p in sorted(glob.glob(pattern)):
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            scene_images.append(os.path.abspath(p))

creative_brief = data.get("creative_brief", {})
product_analysis = data.get("product_analysis", {})

timings["1_load_data"] = round(time.time() - t1, 2)
print(f"=== PHASE 1: 数据加载 ({timings['1_load_data']}s) ===")
print(f"  产品图: {len(product_images)}张")
print(f"  现有场景图: {len(scene_images)}张")
print(f"  创意简报: {'有' if creative_brief else '无'}")
print(f"  产品分析: {'有' if product_analysis else '无'}")

# ── PHASE 2: C1 — 图片管线 ──────────────────────────────────
t2 = time.time()
print(f"\n=== PHASE 2: C1 图片生成管线 ===")

from services.pipeline_bridge import plan_to_images

c1_result = plan_to_images(
    product_images=product_images,
    industry="鞋类",
    platforms=["douyin", "xiaohongshu"],
    creative_brief=creative_brief,
    product_analysis=product_analysis,
    skip_analysis=True,  # Use cached analysis data to stay fast
)

timings["2_c1_images"] = round(time.time() - t2, 2)
print(f"\n  C1 总耗时: {timings['2_c1_images']}s")
print(f"  生成场景: {len(c1_result['scene_paths'])}张")
print(f"  合成套图: {c1_result['total_images']}张")
for comp in c1_result["composite_paths"][:6]:
    print(f"    -> {os.path.basename(comp['path'])} ({comp['platform']})")

# ── PHASE 3: C2 — 脚本生成 ─────────────────────────────────
t3 = time.time()
from services.pipeline_bridge import plan_to_script

script = plan_to_script(plan, industry="鞋类", script_type="with_cart")
timings["3_script_gen"] = round(time.time() - t3, 2)
print(f"\n=== PHASE 3: C2 脚本生成 ({timings['3_script_gen']}s) ===")
print(f"  标题: {script.title}")
print(f"  Beats: {len(script.beats)}")
print(f"  总时长: {script.total_duration_s:.1f}s")

# ── PHASE 4: C2 — 素材管线 ─────────────────────────────────
t4 = time.time()
from services.pipeline_bridge import _build_ref_analysis
from builders.asset_pipeline import AssetPipeline

# Use C1 composited images as the PRIMARY scene pool for asset matching
# (C1 composites are brand-themed, old scenes are fallback)
c1_scene_images = [c["path"] for c in c1_result["composite_paths"] if c["platform"] == "douyin"]
all_scene_images = c1_scene_images + list(scene_images)

ref_analysis = _build_ref_analysis(plan, all_scene_images, creative_brief=creative_brief)

output_dir = os.path.join(Config.DATA_DIR, "videos", "e2e_" + time.strftime("%H%M%S"))
os.makedirs(output_dir, exist_ok=True)
assets_dir = os.path.join(output_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)

asset_pipeline = AssetPipeline(assets_dir=assets_dir)
user_assets = list(product_images) + all_scene_images
asset_plan = asset_pipeline.resolve(script, ref_analysis, user_assets)
summary = asset_pipeline.summary(asset_plan)
timings["4_asset_pipeline"] = round(time.time() - t4, 2)

print(f"\n=== PHASE 4: 素材管线 ({timings['4_asset_pipeline']}s) ===")
print(f"  本地素材: {summary['local_assets']}/{summary['total_beats']}, 需生成: {summary['generation_needed']}")
for beat_idx, ap in sorted(asset_plan.items()):
    path = ap.matched_asset.file_path if ap.matched_asset else "NONE"
    fname = os.path.basename(str(path)) if path and path != "NONE" else "NONE"
    source = ap.matched_asset.source if ap.matched_asset else "?"
    print(f"    Beat{beat_idx}: {fname[:60]} [{source}]")

# ── PHASE 5: C2 — 故事板 + HTML ─────────────────────────────
t5 = time.time()
from builders.assembly_engine import AssemblyEngine
from builders.composition_builder import CompositionBuilder, StoryboardConfig
from services.pipeline_bridge import _PLATFORM_DIMENSIONS, _VIDEO_TYPE_TO_COMPONENT_SET

component_set = _VIDEO_TYPE_TO_COMPONENT_SET.get("product_promo", "ecommerce")
width, height = _PLATFORM_DIMENSIONS.get("douyin", _PLATFORM_DIMENSIONS["default"])

assembler = AssemblyEngine(
    output_dir=output_dir, tts_voice="zh-CN-YunxiNeural", tts_speed=1.15,
    canvas_width=width, canvas_height=height, component_set=component_set,
)
storyboard = assembler._build_storyboard(script, asset_plan, "", "", ref_analysis)

sb_config = StoryboardConfig(
    scenes=storyboard["scenes"], audio_src=storyboard.get("audio_src", ""),
    bgm_src=storyboard.get("bgm_src", ""), global_overlays=storyboard.get("global_overlays", {}),
    metadata=storyboard.get("metadata", {}), style=storyboard.get("style", {}),
)
builder = CompositionBuilder(component_registry=assembler._component_registry)
html = builder.build(sb_config)
html_path = os.path.join(output_dir, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
timings["5_html_gen"] = round(time.time() - t5, 2)

html_kb = len(html.encode("utf-8")) / 1024
print(f"\n=== PHASE 5: HTML生成 ({timings['5_html_gen']}s) ===")
print(f"  大小: {html_kb:.1f}KB, {html.count(chr(10))}行")
print(f"  输出: {html_path}")

# ── PHASE 6: 验证 ──────────────────────────────────────────
t6 = time.time()
checks = {
    "DOCTYPE": "<!doctype html>" in html.lower(),
    "GSAP_CDN": "gsap" in html and ("cdnjs" in html or "jsdelivr" in html),
    "Brand_primary": "--brand-primary" in html,
    "Brand_accent": "--brand-accent" in html,
    "Hook_reveal": "hr-" in html,
    "CTA_outro": "cta-" in html,
    "Scan_overlay": "scanOverlay" in html,
    "Progress_bar": "progressFill" in html,
    "GSAP_timeline": "gsap.timeline" in html,
    "Audio_element": "<audio" in html or "narration" in html,
    "Scene_visible": "scene_0" in html,
    "Has_C1_images": any(os.path.basename(c["path"]) in html for c in c1_result["composite_paths"][:3]),
}
eco_components = {
    "hook-reveal": "hr-" in html,
    "feature-highlight": "fh-" in html,
    "scene-lifestyle": "sl-" in html,
    "before-after": "ba-" in html,
    "trust-signal": "ts-" in html,
    "cta-outro": "cta-" in html,
}
timings["6_validation"] = round(time.time() - t6, 2)
total_time = round(time.time() - total_start, 2)

print(f"\n=== PHASE 6: 验证 ({timings['6_validation']}s) ===")
for k, v in checks.items():
    print(f"  {'✓' if v else '✗'} {k}")
print(f"\n  电商组件:")
for comp, found in eco_components.items():
    print(f"  {'✓' if found else '✗'} {comp}")

# ── SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"C1→C2 端到端总耗时: {total_time}s")
print(f"\n各阶段耗时:")
for phase, sec in timings.items():
    pct = sec / total_time * 100 if total_time > 0 else 0
    bar = "#" * int(pct / 2)
    print(f"  {phase:25s}: {sec:5.1f}s ({pct:4.0f}%) {bar}")

print(f"\n质量记分卡:")
scorecard = {
    "C1_场景生成": len(c1_result["scene_paths"]),
    "C1_合成套图": c1_result["total_images"],
    "C2_脚本结构": len(script.beats),
    "C2_素材匹配": f"{summary['local_assets']}/{summary['total_beats']}",
    "C2_组件渲染": sum(1 for v in eco_components.values() if v),
    "C2_验证通过": f"{sum(1 for v in checks.values() if v)}/{len(checks)}",
}
for k, v in scorecard.items():
    print(f"  {k}: {v}")

# ── SAVE ─────────────────────────────────────────────────────
bench = {
    "total_time_s": total_time,
    "phases": timings,
    "output_dir": output_dir,
    "html_path": html_path,
    "c1": {
        "scene_count": len(c1_result["scene_paths"]),
        "composite_count": c1_result["total_images"],
        "composites": c1_result["composite_paths"],
    },
    "c2": {
        "html_size_kb": html_kb,
        "script_beats": len(script.beats),
        "script_duration_s": script.total_duration_s,
        "validation_passed": sum(1 for v in checks.items() if v),
        "validation_total": len(checks),
        "eco_components": sum(1 for v in eco_components.values() if v),
    },
    "scorecard": scorecard,
}
bench_path = os.path.join(output_dir, "benchmark_e2e.json")
with open(bench_path, "w", encoding="utf-8") as f:
    json.dump(bench, f, ensure_ascii=False, indent=2)
print(f"\n基准数据: {bench_path}")
print(f"HTML文件: {html_path}")
print(f"C1合成图: {c1_result['output_dir']}")

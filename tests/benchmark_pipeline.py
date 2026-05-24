"""Benchmark: Run full pipeline with real timing data at every stage."""
import time, json, os, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"C:\Users\Administrator\visual-hub")
sys.path.insert(0, r"d:\auto-video-platform")
os.chdir(r"C:\Users\Administrator\visual-hub")

from config import Config

timings = {}
total_start = time.time()

# ── PHASE 1: Load data ──────────────────────────────────────
t1 = time.time()
TEST_DATA = os.path.join(Config.DATA_DIR, "pipeline_test_v8.json")
with open(TEST_DATA, "r", encoding="utf-8") as f:
    data = json.load(f)
plan = data["plans"][0]
product_images = [p for p in data.get("image_paths", []) if os.path.exists(p)]
scene_images = []
for pattern in ["data/scenes/generated/*.png", "data/scenes/*.png"]:
    for p in sorted(glob.glob(pattern)):
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            scene_images.append(os.path.abspath(p))
timings["1_load_data"] = round(time.time() - t1, 2)

print(f"=== PHASE 1: 数据加载 ({timings['1_load_data']}s) ===")
print(f"  产品图: {len(product_images)}张")
print(f"  场景图: {len(scene_images)}张")
for p in product_images:
    print(f"    -> {os.path.basename(p)} ({os.path.getsize(p)//1024}KB)")

# ── PHASE 2: Product Analysis (read from cached) ─────────────
t2 = time.time()
pa = data.get("product_analysis", {})
cb = data.get("creative_brief", {})
if pa:
    print(f"\n=== PHASE 2: 产品分析结果 ===")
    print(f"  品类: {pa.get('category','?')} / {pa.get('sub_category','?')}")
    print(f"  风格: {pa.get('style_keywords',[])}")
    print(f"  材质: {pa.get('materials',[])}")
    print(f"  受众: {pa.get('target_audience',{})}")
    print(f"  颜色: {[(c['name'], c['hex_guess']) for c in pa.get('colors',[])]}")
    print(f"  卖点: {pa.get('key_features',[])}")
    print(f"  质感: {pa.get('texture_notes','')[:80]}")
if cb:
    print(f"\n  创意概念: {cb.get('concept_name','?')}")
    print(f"  概念故事: {cb.get('concept_story','')[:80]}")
    print(f"  情绪: {cb.get('mood_keywords',[])}")
    print(f"  场景数: {len(cb.get('scenes',[]))}")
    for s in cb.get("scenes", []):
        print(f"    - {s['scene_name']}: {s['description'][:60]}...")
timings["2_read_analysis"] = round(time.time() - t2, 2)

# ── PHASE 3: Script generation ───────────────────────────────
t3 = time.time()
from services.pipeline_bridge import plan_to_script
script = plan_to_script(plan, industry="鞋类", script_type="with_cart")
timings["3_script_gen"] = round(time.time() - t3, 2)
print(f"\n=== PHASE 3: 脚本生成 ({timings['3_script_gen']}s) ===")
print(f"  标题: {script.title}")
print(f"  Beats: {len(script.beats)}")
for b in script.beats:
    l2 = getattr(b, "audio_l2_text", "") or ""
    print(f"    Beat{b.index}: {b.text[:50]}... ({b.duration_s:.1f}s, {b.emotion})")
print(f"  Outro: {script.outro.text[:60]}...")
print(f"  总时长: {script.total_duration_s:.1f}s")

# ── PHASE 4: Asset pipeline ──────────────────────────────────
t4 = time.time()
from services.pipeline_bridge import _build_ref_analysis
from builders.asset_pipeline import AssetPipeline
ref_analysis = _build_ref_analysis(plan, scene_images, creative_brief=data.get("creative_brief"))
output_dir = os.path.join(Config.DATA_DIR, "videos", "bench_" + time.strftime("%H%M%S"))
os.makedirs(output_dir, exist_ok=True)
assets_dir = os.path.join(output_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)
asset_pipeline = AssetPipeline(assets_dir=assets_dir)
user_assets = list(product_images) + list(scene_images)
asset_plan = asset_pipeline.resolve(script, ref_analysis, user_assets)
summary = asset_pipeline.summary(asset_plan)
timings["4_asset_pipeline"] = round(time.time() - t4, 2)
print(f"\n=== PHASE 4: 素材管线 ({timings['4_asset_pipeline']}s) ===")
print(f"  Beats: {summary['total_beats']}, 本地素材: {summary['local_assets']}, 需生成: {summary['generation_needed']}")
for beat_idx, ap in sorted(asset_plan.items()):
    asset = ap.matched_asset
    path = asset.file_path if asset else "NONE"
    fname = os.path.basename(str(path)) if path and path != "NONE" else "NONE"
    print(f"    Beat{beat_idx}: {fname}")

# ── PHASE 5: Storyboard ──────────────────────────────────────
t5 = time.time()
from builders.assembly_engine import AssemblyEngine
from services.pipeline_bridge import _PLATFORM_DIMENSIONS, _VIDEO_TYPE_TO_COMPONENT_SET
component_set = _VIDEO_TYPE_TO_COMPONENT_SET.get("product_promo", "ecommerce")
width, height = _PLATFORM_DIMENSIONS.get("douyin", _PLATFORM_DIMENSIONS["default"])
assembler = AssemblyEngine(
    output_dir=output_dir, tts_voice="zh-CN-YunxiNeural", tts_speed=1.15,
    canvas_width=width, canvas_height=height, component_set=component_set,
)
storyboard = assembler._build_storyboard(script, asset_plan, "", "", ref_analysis)
timings["5_storyboard"] = round(time.time() - t5, 2)
print(f"\n=== PHASE 5: 故事板 ({timings['5_storyboard']}s) ===")
print(f"  Canvas: {width}x{height}, 组件集: {component_set}")
print(f"  Storyboard场景: {len(storyboard['scenes'])}")
for i, scene in enumerate(storyboard["scenes"]):
    img = os.path.basename(str(scene.get("config", {}).get("img_src", ""))) or "NONE"
    print(f"    Scene{i}: {scene['component']} ({scene['duration']:.1f}s) img={img}")

# ── PHASE 6: HTML generation ─────────────────────────────────
t6 = time.time()
from builders.composition_builder import CompositionBuilder, StoryboardConfig
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
timings["6_html_gen"] = round(time.time() - t6, 2)
html_kb = len(html.encode("utf-8")) / 1024
html_lines = html.count("\n")
print(f"\n=== PHASE 6: HTML生成 ({timings['6_html_gen']}s) ===")
print(f"  大小: {html_kb:.1f}KB, {html_lines}行")
print(f"  输出: {html_path}")

# ── PHASE 7: Validation ──────────────────────────────────────
t7 = time.time()
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
    "No_AI_leak": not any(c in html for c in ["social-frame", "glitch-transition", "zoom-analyze", "compare-split"]),
}
eco_components = {
    "hook-reveal": "hr-" in html,
    "feature-highlight": "fh-" in html,
    "scene-lifestyle": "sl-" in html,
    "before-after": "ba-" in html,
    "trust-signal": "ts-" in html,
    "cta-outro": "cta-" in html,
}
timings["7_validation"] = round(time.time() - t7, 2)
total_time = round(time.time() - total_start, 2)

print(f"\n=== PHASE 7: 验证 ({timings['7_validation']}s) ===")
for k, v in checks.items():
    print(f"  {'✓' if v else '✗'} {k}")
print(f"\n  电商组件命中:")
for comp, found in eco_components.items():
    print(f"  {'✓' if found else '✗'} {comp}")

# ── SUMMARY ──────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"总耗时: {total_time}s")
print(f"\n各阶段耗时占比:")
for phase, sec in timings.items():
    pct = sec / total_time * 100 if total_time > 0 else 0
    bar = "#" * int(pct / 2)
    print(f"  {phase:25s}: {sec:5.1f}s ({pct:4.0f}%) {bar}")

# ── QUALITY SCORECARD ────────────────────────────────────────
print(f"\n{'='*60}")
print("质量记分卡:")
scorecard = {
    "输入完整性": 10 if len(product_images) >= 3 else 5,
    "品类准确度": 8 if pa.get("category") else 0,
    "创意独特性": 8 if cb.get("concept_name") else 0,
    "脚本结构": 8 if len(script.beats) >= 5 else 4,
    "素材匹配": 10 if summary["local_assets"] >= summary["total_beats"] * 0.7 else 5,
    "组件渲染": sum(1 for v in eco_components.values() if v),
    "HTML完整度": sum(1 for v in checks.values() if v),
}
for k, v in scorecard.items():
    print(f"  {k}: {v}")
print(f"  总体验证通过: {sum(1 for v in checks.values() if v)}/12")

# ── SAVE ─────────────────────────────────────────────────────
bench = {
    "total_time_s": total_time,
    "phases": timings,
    "output_dir": output_dir,
    "html_path": html_path,
    "html_size_kb": html_kb,
    "html_lines": html_lines,
    "validation": {k: v for k, v in checks.items()},
    "eco_components": eco_components,
    "scorecard": scorecard,
    "script_beats": len(script.beats),
    "script_duration_s": script.total_duration_s,
    "product_images": len(product_images),
    "scene_images": len(scene_images),
}
bench_path = os.path.join(output_dir, "benchmark.json")
with open(bench_path, "w", encoding="utf-8") as f:
    json.dump(bench, f, ensure_ascii=False, indent=2)
print(f"\n基准数据: {bench_path}")
print(f"HTML文件: {html_path}")

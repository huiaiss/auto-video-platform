"""Full pipeline integration test — validates all 8 stages end-to-end."""
import os, sys, time, json, traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# Load .env
env_path = os.path.join(ROOT, ".env")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

OUTPUT_DIR = os.path.join(ROOT, "output", "_test_" + time.strftime("%Y%m%d_%H%M%S"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

REF_IMAGE = os.path.join(ROOT, "output", "ep2_assets", "ep2_img1_store_sign.png")
VIDEO_TYPE = "ai_flaw_detect"
TOPIC = "文字乱码识别"
TTS_VOICE = "zh-CN-YunxiNeural"

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = {}
stage_times = {}

def report(stage_num, name, ok, detail="", elapsed=0):
    icon = PASS if ok else FAIL
    results[stage_num] = {"name": name, "ok": ok, "detail": detail, "elapsed": round(elapsed, 1)}
    stage_times[stage_num] = round(elapsed, 1)
    status = "通过" if ok else "失败"
    print(f"  {icon} 阶段{stage_num} [{name}]: {status} ({stage_times[stage_num]}s)")
    if detail and not ok:
        print(f"      原因: {detail[:200]}")

def main():
    print("=" * 60)
    print("  Auto Video Platform — 8-Stage Pipeline Test")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Ref: {REF_IMAGE}")
    print("=" * 60)

    if not os.path.exists(REF_IMAGE):
        print(f"\n{FAIL} 参考图不存在: {REF_IMAGE}")
        return

    # ── Import pipeline ──
    print("\n[0] Loading Pipeline...")
    from pipeline import VideoPipeline
    pipeline = VideoPipeline()
    print(f"  {PASS} Pipeline loaded (LLM=DeepSeek, TTS=Edge TTS)")

    # ════════════════════════════════════════════
    # Stage 1: Reference Analysis
    # ════════════════════════════════════════════
    print("\n── Stage 1: 参考图分析 ──")
    t0 = time.time()
    ref_analysis = {}
    try:
        ref_analysis = pipeline._analyze_ref(REF_IMAGE)
        elapsed = time.time() - t0
        desc = ref_analysis.get("description", "")
        ok = bool(desc)
        report(1, "参考图分析", ok, desc[:150], elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(1, "参考图分析", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 2: Script Generation
    # ════════════════════════════════════════════
    print("\n── Stage 2: AI脚本生成 ──")
    t0 = time.time()
    script = None
    try:
        script = pipeline._generate_script(VIDEO_TYPE, TOPIC, ref_analysis, None, "")
        elapsed = time.time() - t0
        ok = script is not None and len(script.beats) >= 3
        detail = f"标题={script.title}, Beats={len(script.beats)}, 时长={script.total_duration_s}s"
        report(2, "AI脚本生成", ok, detail, elapsed)
        if ok:
            for b in script.beats[:3]:
                print(f"       Beat{b.index}: {b.text[:60]}...")
    except Exception as e:
        elapsed = time.time() - t0
        report(2, "AI脚本生成", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 3: Quality Check
    # ════════════════════════════════════════════
    print("\n── Stage 3: 质量检查 ──")
    t0 = time.time()
    try:
        if script is None:
            raise RuntimeError("No script from Stage 2")
        report_obj = pipeline.quality_checker.check(script, VIDEO_TYPE)
        if not report_obj.passed:
            script = pipeline.quality_checker.auto_fix(script, report_obj)
            report_obj = pipeline.quality_checker.check(script, VIDEO_TYPE)
        elapsed = time.time() - t0
        n_violations = len(report_obj.violations)
        ok = report_obj.passed or n_violations <= 2
        detail = f"得分={report_obj.score}, 通过={report_obj.passed}, 违规={n_violations}"
        report(3, "质量检查", ok, detail, elapsed)
        if report_obj.warnings:
            for w in report_obj.warnings[:3]:
                print(f"       {WARN} {w.rule}: {w.detail[:80]}")
    except Exception as e:
        elapsed = time.time() - t0
        report(3, "质量检查", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 4: TTS Narration
    # ════════════════════════════════════════════
    print("\n── Stage 4: TTS配音 ──")
    t0 = time.time()
    tts_output = None
    try:
        if script is None:
            raise RuntimeError("No script from Stage 2")
        tts_output = pipeline._build_tts(script, OUTPUT_DIR, voice=TTS_VOICE, speed=1.1)
        elapsed = time.time() - t0
        ok = tts_output is not None and os.path.exists(tts_output.audio_path)
        detail = f"音频={tts_output.audio_path}, SRT={tts_output.srt_path}"
        report(4, "TTS配音", ok, detail, elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(4, "TTS配音", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 5: Asset Matching
    # ════════════════════════════════════════════
    print("\n── Stage 5: 素材匹配 ──")
    t0 = time.time()
    asset_plan = {}
    try:
        if script is None:
            raise RuntimeError("No script from Stage 2")
        asset_plan = pipeline._resolve_assets(script, ref_analysis, REF_IMAGE)

        from builders.asset_pipeline import AssetPipeline
        ap = AssetPipeline(assets_dir=os.path.join(OUTPUT_DIR, "assets"))
        summary = ap.summary(asset_plan)
        gen_needed = summary.get("generation_needed", 0)
        if gen_needed > 0:
            print(f"       素材缺口={gen_needed}, 执行AI生成...")
            asset_plan = ap.generate_missing(asset_plan)
            summary = ap.summary(asset_plan)

        elapsed = time.time() - t0
        local = summary.get("local_assets", 0)
        ai_gen = summary.get("ai_generated", 0)
        ok = summary.get("total_beats", 0) > 0
        detail = f"总Beats={summary.get('total_beats')}, 本地={local}, AI生成={ai_gen}, Stock={summary.get('stock_fallback')}"
        report(5, "素材匹配", ok, detail, elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(5, "素材匹配", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 6: HTML Assembly
    # ════════════════════════════════════════════
    print("\n── Stage 6: HTML组装 ──")
    t0 = time.time()
    result = None
    try:
        if not asset_plan:
            raise RuntimeError("No asset plan from Stage 5")
        from builders.assembly_engine import AssemblyEngine
        assembler = AssemblyEngine(
            output_dir=OUTPUT_DIR,
            tts_voice=TTS_VOICE,
            tts_speed=1.1,
        )
        result = assembler.assemble(script, asset_plan, "", ref_analysis)
        elapsed = time.time() - t0
        ok = result is not None and os.path.exists(result.html_path)
        detail = f"HTML={result.html_path}"
        report(6, "HTML组装", ok, detail, elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(6, "HTML组装", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 7: MP4 Render
    # ════════════════════════════════════════════
    print("\n── Stage 7: MP4渲染 ──")
    t0 = time.time()
    mp4_path = ""
    try:
        from builders.chromium_renderer import ChromiumRenderer
        renderer = ChromiumRenderer()
        mp4_path = renderer.render(
            html_dir=OUTPUT_DIR,
            audio_path=result.audio_path if result and os.path.exists(result.audio_path) else "",
            duration_s=result.total_duration_s if result else 30,
            output_path=os.path.join(OUTPUT_DIR, "output.mp4"),
        )
        elapsed = time.time() - t0
        ok = mp4_path and os.path.exists(mp4_path)
        size_mb = os.path.getsize(mp4_path) / (1024 * 1024) if ok else 0
        detail = f"MP4={mp4_path}, 大小={size_mb:.1f}MB"
        report(7, "MP4渲染", ok, detail, elapsed)
    except FileNotFoundError as e:
        elapsed = time.time() - t0
        report(7, "MP4渲染", False, f"Chromium未安装: {e}", elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(7, "MP4渲染", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Stage 8: Jianying Export
    # ════════════════════════════════════════════
    print("\n── Stage 8: 剪映草稿导出 ──")
    t0 = time.time()
    try:
        if result is None:
            raise RuntimeError("No assembly result from Stage 6")
        jy_path = assembler.export_jianying(result) or ""
        elapsed = time.time() - t0
        ok = bool(jy_path) and os.path.exists(jy_path)
        detail = f"草稿={jy_path}" if ok else "跳过（可选阶段）"
        report(8, "剪映草稿导出", ok, detail, elapsed)
    except Exception as e:
        elapsed = time.time() - t0
        report(8, "剪映草稿导出", False, str(e), elapsed)
        traceback.print_exc()

    # ════════════════════════════════════════════
    # Summary
    # ════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results.values() if r["ok"])
    total = len(results)
    total_time = sum(stage_times.values())
    for num in sorted(results.keys()):
        r = results[num]
        icon = PASS if r["ok"] else FAIL
        print(f"  {icon} 阶段{num} [{r['name']}]: {r['elapsed']}s")
    print(f"\n  总计: {passed}/{total} 通过, 总耗时 {total_time:.1f}s")
    print(f"  输出目录: {OUTPUT_DIR}")

    # Write report
    report_path = os.path.join(OUTPUT_DIR, "test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "passed": passed, "total": total,
                    "total_time_s": total_time, "output_dir": OUTPUT_DIR},
                   f, ensure_ascii=False, indent=2)
    print(f"  报告: {report_path}")

    if passed == total:
        print(f"\n  {PASS}{PASS}{PASS} 全部8个阶段测试通过!")
    else:
        print(f"\n  {WARN} 有 {total - passed} 个阶段未通过，请检查日志。")

if __name__ == "__main__":
    main()

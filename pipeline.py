#!/usr/bin/env python
# Auto Video Platform - AI Video Pipeline
# Pipeline: Stage0???? -> Stage1?? -> Stage2????->?? -> Stage3??


import os, json, glob, subprocess, sys, shutil
from pathlib import Path

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUTPUT = os.path.join(ROOT, "output")


HDR_TONEMAP = (
    "zscale=t=linear:npl=100,format=gbrpf32le,"
    "zscale=p=bt709,tonemap=hable:desat=2,"
    "zscale=t=bt709:m=bt709:r=tv:f=lanczos,format=yuv420p"
)


def run_ff(cmd, timeout=600):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          encoding="utf-8", errors="replace")


def ffprobe_get(path, key, stream="format"):
    r = run_ff(["ffprobe", "-v", "error", "-show_entries",
                f"{stream}={key}", "-of", "csv=p=0", path])
    return r.stdout.strip()


def detect_hdr(path):
    pix = ffprobe_get(path, "pix_fmt", "stream")
    trc = ffprobe_get(path, "color_transfer", "stream")
    return "yuv420p10le" in pix or "arib-std-b67" in trc or "hlg" in trc.lower()


def run_audit(audit_script, *args):
    cmd = [sys.executable, audit_script] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.stdout.strip():
        for line in r.stdout.split("\n"):
            if any(x in line for x in ["[PASS]", "[FAIL]"]):
                try:
                    print(line)
                except UnicodeEncodeError:
                    line = line.encode("gbk", errors="replace").decode("gbk")
                    print(line)
    return r.returncode == 0


# ====== Stage 1 ======

def stage1(footage_pattern, brand_key="taizhou_longjiang"):
    print("=" * 60)
    print("Stage 1/3 -- ????")
    print("=" * 60)
    out_dir = os.path.join(OUTPUT, "stage1")
    os.makedirs(out_dir, exist_ok=True)

    # 1.1 Scan
    print("\n[1.1] ????")
    video_files = sorted(glob.glob(footage_pattern))
    if not video_files:
        print(f"  No footage: {footage_pattern}")
        return False
    print(f"  Found {len(video_files)} files")
    for vf in video_files:
        dur = float(ffprobe_get(vf, "duration") or 0)
        pix = ffprobe_get(vf, "pix_fmt", "stream") or "?"
        hdr = detect_hdr(vf)
        print(f"    {Path(vf).name}: {dur:.1f}s, {pix}, {'HDR' if hdr else 'SDR'}")

    # 1.2 HDR->SDR
    print("\n[1.2] HDR->SDR ????")
    sdr_files = []
    for vf in video_files:
        if detect_hdr(vf):
            stem = Path(vf).stem
            sdr_path = os.path.join(out_dir, f"_sdr_{stem}.mp4")
            if os.path.exists(sdr_path) and os.path.getsize(sdr_path) > 1000:
                print(f"  (cached) {stem}")
            else:
                print(f"  Mapping {stem}...")
                r = run_ff(["ffmpeg", "-y", "-i", vf,
                    "-vf", HDR_TONEMAP,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-profile:v", "main",
                    "-colorspace", "bt709", "-movflags", "+faststart",
                    "-an", sdr_path], timeout=1200)
                if r.returncode != 0:
                    print(f"  FAILED: {r.stderr[-200:]}")
                    return False
            sdr_files.append(sdr_path)
        else:
            sdr_files.append(vf)
    print(f"  {len(sdr_files)} ready")

    # 1.3 Scene detection + scoring
    print("\n[1.3] ???? + ??")
    all_clips = []
    for si, sdr in enumerate(sdr_files):
        stem = Path(video_files[si]).stem
        dur = float(ffprobe_get(sdr, "duration") or 0)
        if dur < 1:
            continue
        r = run_ff(["ffmpeg", "-i", sdr,
            "-vf", "select='gt(scene,0.3)',showinfo",
            "-f", "null", "-"])
        change_pts = {0.0, dur}
        for line in (r.stderr + r.stdout).split("\n"):
            if "pts:" in line:
                try:
                    pts = float(line.split("pts:")[1].strip().split()[0])
                    if 0.3 < pts < dur - 0.3:
                        change_pts.add(pts)
                except:
                    pass
        change_pts = sorted(change_pts)
        for i in range(len(change_pts) - 1):
            st, et = change_pts[i], change_pts[i+1]
            cd = et - st
            if cd < 0.5:
                continue
            if cd > 10:
                for j in range(0, int(cd), 5):
                    cst = st + j
                    cet = min(st + j + 5, et)
                    if cet - cst >= 1.5:
                        all_clips.append({"file": sdr, "start": cst, "end": cet,
                                          "duration": cet - cst, "source_idx": si,
                                          "source_name": stem})
            else:
                all_clips.append({"file": sdr, "start": st, "end": et,
                                  "duration": cd, "source_idx": si,
                                  "source_name": stem})

    import cv2, numpy as np
    for clip in all_clips:
        clip["score"] = _score_segment(clip["file"], clip["start"], clip["end"])
    all_clips.sort(key=lambda c: c["score"], reverse=True)
    print(f"  Candidate clips: {len(all_clips)}")
    if all_clips:
        print(f"  Best: {all_clips[0]['source_name']} @ "
              f"{all_clips[0]['start']:.1f}s ({all_clips[0]['score']:.3f})")

    # 1.4 Selection
    print("\n[1.4] ???? Top N")
    selected = _select_top_clips(all_clips, target_dur=(32, 65), max_per_source=3)
    print(f"  Selected {len(selected)} clips from "
          f"{len(set(c['source_idx'] for c in selected))} sources")
    print(f"  Total duration: {sum(c['duration'] for c in selected):.1f}s")
    for c in selected:
        print(f"    {c['source_name']} @ {c['start']:.1f}-{c['end']:.1f}s "
              f"({c['duration']:.1f}s, score={c['score']:.3f})")

    # 1.5 Concat (with fade transitions between clips for audit scene detection)
    print("\n[1.5] ?? -> roughcut.mp4")
    # First extract individual clips with trimmed ends
    clip_paths = []
    for i, clip in enumerate(selected):
        clip_path = os.path.join(out_dir, f"_clip_{i:03d}.mp4")
        r = run_ff(["ffmpeg", "-y", "-ss", str(clip["start"]),
            "-i", clip["file"],
            "-t", str(clip["duration"]),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-colorspace", "bt709",
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
            "-an", clip_path], timeout=300)
        if r.returncode != 0:
            print(f"  Clip {i} FAILED: {r.stderr[-200:]}")
            return False
        clip_paths.append(clip_path)

    # Concat: use xfade transitions instead of 0.25s black frames
    roughcut = os.path.join(out_dir, "roughcut.mp4")
    XFADE_DUR = 0.3  # short crossfade to conserve duration

    if len(clip_paths) == 1:
        shutil.copy2(clip_paths[0], roughcut)
    else:
        # Get durations of each clip
        clip_durs = []
        for cp in clip_paths:
            d = float(ffprobe_get(cp, "duration") or 0)
            clip_durs.append(d if d > 0 else 5.0)  # fallback 5s if ffprobe fails
        # Build xfade filter chain
        inputs = []
        for p in clip_paths:
            inputs.extend(["-i", p])
        
        filter_parts = []
        for i in range(len(clip_paths) - 1):
            if i == 0:
                offset = clip_durs[0] - XFADE_DUR
                filter_parts.append(
                    f"[0:v]setpts=PTS-STARTPTS,fps=30[v0];"
                    f"[1:v]setpts=PTS-STARTPTS,fps=30[v1];"
                    f"[v0][v1]xfade=transition=fade:duration={XFADE_DUR}:offset={offset:.2f}[vx0]"
                )
            else:
                offset = offset + clip_durs[i] - XFADE_DUR
                filter_parts.append(
                    f"[{i+1}:v]setpts=PTS-STARTPTS,fps=30[v{i+1}];"
                    f"[vx{i-1}][v{i+1}]xfade=transition=fade:duration={XFADE_DUR}:offset={offset:.2f}[vx{i}]"
                )
        
        filter_chain = ";".join(filter_parts)
        last_tag = f"[vx{len(clip_paths)-2}]"
        
        r = run_ff(["ffmpeg", "-y"] + inputs + [
            "-filter_complex", filter_chain,
            "-map", last_tag,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-colorspace", "bt709", "-movflags", "+faststart",
            roughcut], timeout=600)
        if r.returncode != 0:
            print(f"  Concat FAILED: {r.stderr[-300:]}")
            return False
    if r.returncode != 0:
        print(f"  Concat FAILED: {r.stderr[-200:]}")
        return False

    final_dur = float(ffprobe_get(roughcut, "duration") or 0)
    size_mb = os.path.getsize(roughcut) / 1024 / 1024
    print(f"\n  roughcut.mp4: {final_dur:.1f}s, {size_mb:.1f}MB")
    print(f"  Stage 1 done: {roughcut}")

    # Cleanup temp SDR files only (keep clips for now)
    for f in sdr_files:
        if f.startswith(out_dir) and os.path.exists(f):
            os.remove(f)

    # Audit
    print("\n" + "=" * 60)
    print("Run audit: audit_roughcut.py")
    print("=" * 60)
    audit_ok = run_audit(
        os.path.join(ROOT, "auditors", "audit_roughcut.py"),
        roughcut
    )
    if audit_ok:
        print("\nStage 1 PASS -- audit 5/5")
        return True
    else:
        print("\nStage 1 FAIL -- audit rejected")
        return False


def _score_segment(video_path, start, end):
    import cv2, numpy as np
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.release()
    scores = []
    for offset in [-0.3, 0, 0.3]:
        t = int((((start + end) / 2) + offset) * fps)
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, t))
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lap = float(np.var(cv2.Laplacian(gray, cv2.CV_64F)))
        sharp = min(lap / 500, 1.0)
        mean_b = float(np.mean(gray))
        bright = 1.0 - abs(mean_b - 128) / 128
        h, w = gray.shape
        ch, cw = h // 4, w // 4
        center = float(np.mean(gray[ch:3*ch, cw:3*cw]))
        edge = float(np.mean(np.concatenate([
            gray[:ch,:].ravel(), gray[3*h//4:,:].ravel(),
            gray[:,:cw].ravel(), gray[:,3*w//4:].ravel()
        ])))
        comp = min(abs(center - edge) / 40, 1.0)
        scores.append(sharp * 0.4 + bright * 0.3 + comp * 0.3)
    return float(np.mean(scores)) if scores else 0.0


def _select_top_clips(clips, min_sources=3, target_dur=(30, 60), max_per_source=2):
    if not clips:
        return []
    by_source = {}
    for c in clips:
        by_source.setdefault(c["source_idx"], []).append(c)
    candidates = []
    for si, sclips in by_source.items():
        sclips.sort(key=lambda x: x["score"], reverse=True)
        candidates.extend(sclips[:max_per_source])
    candidates.sort(key=lambda x: x["score"], reverse=True)
    selected = []
    used_sources = set()
    total_dur = 0
    for c in candidates:
        if len(used_sources) >= min_sources:
            break
        if c["source_idx"] not in used_sources and total_dur + c["duration"] <= target_dur[1]:
            selected.append(c)
            used_sources.add(c["source_idx"])
            total_dur += c["duration"]
    # Phase 2: prefer clips from unused sources first
    for c in candidates:
        if total_dur >= target_dur[0]:
            break
        if c not in selected and total_dur + c["duration"] <= target_dur[1]:
            if c["source_idx"] not in used_sources:
                selected.append(c)
                used_sources.add(c["source_idx"])
                total_dur += c["duration"]
    # Phase 3: fill remaining with any clips
    for c in candidates:
        if total_dur >= target_dur[0]:
            break
        if c not in selected and total_dur + c["duration"] <= target_dur[1]:
            selected.append(c)
            total_dur += c["duration"]
    selected.sort(key=lambda c: (c["source_idx"], c["start"]))
    return selected




def _truncate_text(text, max_len=28):
    """Truncate text at last complete punctuation within max_len, not mid-sentence.

    Supports both Chinese and English punctuation. If no sentence-ending punctuation
    found, falls through to comma, then space, then hard cut at word boundary.
    """
    if len(text) <= max_len:
        return text
    # Try sentence-ending punctuation first (Chinese + English)
    for sep in "。！？；.!?;":
        idx = text.rfind(sep, 0, max_len + 2)
        if idx > max_len * 0.25:  # only cut after meaningful content
            return text[:idx+1]
    # Try comma (Chinese + English)
    for sep in "，,、":
        idx = text.rfind(sep, 0, max_len + 2)
        if idx > max_len * 0.25:
            return text[:idx+1]
    # Try last space
    idx = text.rfind(" ", 0, max_len)
    if idx > max_len * 0.25:
        return text[:idx]
    # Last resort: hard cut at last complete word before limit
    return text[:max_len-1] + "…"


# ====== Stage 2 ======

def stage2(brand_key="taizhou_longjiang", marketing_mode=False):
    print("=" * 60)
    print("Stage 2/3 -- ????")
    print("=" * 60)
    
    out_dir = os.path.join(OUTPUT, "stage2")
    os.makedirs(out_dir, exist_ok=True)
    roughcut = os.path.join(OUTPUT, "stage1", "roughcut.mp4")
    if not os.path.exists(roughcut):
        print(f"  Stage 1 output not found: {roughcut}")
        print("  Run stage1 first!")
        return False
    
    # Load brand data
    from config.brand_loader import get_brand
    brand = get_brand(brand_key)
    print(f"  Brand: {brand.get('brand_name', brand_key)}")
    
    # 2.1 Extract frames from roughcut
    print("\n[2.1] ??")
    dur = float(ffprobe_get(roughcut, "duration") or 30)
    frame_positions = []
    if dur <= 15:
        frame_positions = [3, dur - 2]
    elif dur <= 30:
        frame_positions = [2, dur * 0.33, dur * 0.66, dur - 2]
    else:
        frame_positions = [2, dur * 0.2, dur * 0.4, dur * 0.6, dur * 0.8, dur - 2]
    
    frame_files = []
    for i, pos in enumerate(frame_positions):
        fp = os.path.join(out_dir, f"_frame_{i:02d}.jpg")
        run_ff(["ffmpeg", "-y", "-ss", str(pos), "-i", roughcut,
                "-vframes", "1", "-q:v", "3", fp], timeout=30)
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            frame_files.append(fp)
            print(f"    Frame {i}: {pos:.1f}s ({os.path.getsize(fp)//1024}KB)")
    
    # 2.2 Vision analysis of frames
    print("\n[2.2] ????")
    frame_descriptions = []
    for fp in frame_files:
        desc = _analyze_frame(fp, brand)
        if desc:
            frame_descriptions.append(desc)
            print(f"    {os.path.basename(fp)}: {desc[:80]}...")
    
    # 2.3 Generate script via LLM
    print("\n[2.3] LLM????")
    script = _generate_script_from_frames(frame_descriptions, brand, roughcut, marketing_mode)
    if not script:
        print("  Script generation FAILED")
        return False
    
    # Post-process: clip beat text to max 26 chars at punctuation boundaries
    for b in script.get("beats", []):
        if len(b.get("text", "")) > 26:
            old = b["text"]
            b["text"] = _truncate_text(old, 26)
            if b["text"] != old:
                print(f"    Trimmed beat text: {len(old)} -> {len(b['text'])} chars")
    # Ensure each beat ends with punctuation for TTS completeness
    for b in script.get("beats", []):
        text = b.get("text", "")
        if text and text[-1] not in "。！？，,!?.":
            b["text"] = text + "。"
    # Force brand name into outro text if missing (audit requirement)
    outro = script.get("outro", {})
    brand_name = brand.get("brand_name", "")
    if brand_name and brand_name not in outro.get("text", ""):
        outro_text = outro.get("text", "").rstrip("。！？，,.;!?") + "。" + brand_name + "。"
        script["outro"]["text"] = outro_text
    # Write start_s for each beat (cumulative duration from previous beats)
    t = 0.0
    for b in script.get("beats", []):
        b["start_s"] = round(t, 1)
        t += b.get("duration_s", 3)
    # Also set end_s for convenience
    for b in script.get("beats", []):
        b["end_s"] = round(b["start_s"] + b.get("duration_s", 3), 1)
    # Save script.json
    script_path = os.path.join(out_dir, "script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"  Script saved: {script_path}")
    print(f"  Title: {script.get("title", "")}")
    print(f"  Beats: {len(script.get("beats", []))}")
    print(f"  Duration: {script.get("total_duration_s", 0):.1f}s")
    
    # Audit
    print("\n" + "=" * 60)
    print("Run audit: audit_script.py")
    print("=" * 60)
    audit_ok = run_audit(
        os.path.join(ROOT, "auditors", "audit_script.py"),
        script_path, roughcut
    )
    if audit_ok:
        print("\nStage 2 PASS -- audit 5/5")
        return True
    else:
        print("\nStage 2 FAIL -- audit rejected")
        return False


def _analyze_frame(frame_path, brand):
    """Analyze a single frame using vision model. Extract specific details for script writing."""
    import base64
    with open(frame_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    img_data_url = f"data:image/jpeg;base64,{b64}"

    from generators.llm_providers import get_dispatcher
    dispatcher = get_dispatcher()

    brand_name = brand.get("brand_name", "brand")
    prompt = (
        f"你是工厂设备质检员。仔细看这张{ brand_name }生产现场的图片，列出你看到的所有具体信息：\n\n"
        "1. 画面中心是什么设备/零件？精确的名称和特征（颜色、形状、材质）\n"
        "2. 这个设备/零件在做什么动作？（运行中/静态/被操作/正在加工...）\n"
        "3. 画面上还有什么其他物体？位置关系如何？\n"
        "4. 有什么文字、标签、仪表盘可以读？\n\n"
        "要求：用具体的词汇，不要用'精密设备''工业部件''机械结构'这种笼统话。"
        "比如'飞叉绕线头正在高速旋转，铜线被引导到定子槽内'这种具体描述。\n"
        "输出2-3句中文。"
    )

    try:
        messages = [
            {"role": "system", "content": "你是工厂设备质检员。输出具体、精确的画面描述，使用设备专业术语。不要用笼统词汇。"},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": img_data_url}},
                {"type": "text", "text": prompt},
            ]},
        ]
        resp = dispatcher.chat(messages, model="doubao-seed-1-6-vision-250815")
        if resp and resp.content:
            return resp.content.strip()
        return ""
    except Exception as e:
        print(f"  Vision analysis error: {e}")
        return f"Vision error: {e}"

def _generate_script_from_frames(frame_descriptions, brand, roughcut_path, marketing_mode=False):
    """Generate script.json using LLM."""
    from generators.terms_generator import generate_terms
    dur = float(ffprobe_get(roughcut_path, "duration") or 30)

    from generators.llm_providers import get_dispatcher
    dispatcher = get_dispatcher()

    frame_context = "\n".join(
        f"[Frame{i+1}] {desc}" for i, desc in enumerate(frame_descriptions) if desc
    )

    brand_name = brand.get("brand_name", "Mystery Brand")
    products = ", ".join(p["name"] for p in brand.get("main_products", []))
    must_mention = ", ".join(brand.get("must_mention", []))
    tags = brand.get("tags", [])
    tag_str = ", ".join(tags[:5])
    bgm_style = brand.get("bgm_style", "industrial/electronic")

    if marketing_mode:
        prompt = f"""你是短视频脚本编剧。为 {brand_name} 写一个营销短视频脚本。

## 素材描述（画面分析）
{frame_context}

## 规则
- 时长: {dur:.0f}s，每段 3-6s
- 口语化中文，像朋友聊天
- 禁止套话：品质卓越、行业领先、精益求精、值得信赖
- 开头用痛点问题钩子
- 结尾引导点击/咨询
- **每条文案必须≤26字，且是完整句子** ── 26字以内能说清楚就不要写更长
- **每条文案必须对应一段具体的画面内容，不能是通用套话**
- **每段必须指定 start_s（在整条视频中的起始秒数，从0开始累积）**

## 好文案示例（26字以内，完整句）
✅ "张力不稳就烧线圈，绕线机压不住精度你就亏了" (21字)
✅ "同一台机器铜线上多绕一层，成本多5毛" (19字)
✅ "内行看张力数值，外行才看转速" (16字)
❌ "内行才知道，绕线机省成本的关键，其实就在于精密的张力控制" (29字，超了)

## 输出 JSON
{{
  "title": "标题 15字内",
  "beats": [
    {{
      "index": 1,
      "text": "口播文案（≤26字，完整句）",
      "visual": "对应画面描述",
      "animation": "zoom|fade|slide|pop|pulse|none",
      "emotion": "hook|pain|solution|proof|action",
      "duration_s": 4.0,
      "start_s": 0.0
    }}
  ],
  "outro": {{
    "text": "引导语",
    "visual": "品牌 + CTA",
    "duration_s": 5.0
  }},
  "total_duration_s": {dur:.0f},
  "bgm_style": "{bgm_style}",
  "tags": ["{tag_str}"]
}}
Return ONLY valid JSON, no markdown. 确保每条text≤26字且是完整句。"""
    else:
        prompt = f"""你是短视频脚本编剧。为 {brand_name} 写一个内容分享短视频脚本。

## 素材描述（画面分析）
{frame_context}

## 规则
- 时长: {dur:.0f}s，每段 3-6s
- 口语化中文，像业内人士分享经验
- 禁止营销：不能说"点击"、"免费"、"咨询"
- 开头可以是行业秘密/内行才知道的事
- 结尾引导收藏/转发/关注
- **每条文案必须≤26字，且是完整句子** ── 精炼再精炼
- **每条文案必须对应一段具体的画面内容——把你看到的设备、动作、位置写进文案，不能是通用套话**
- **每段必须指定 start_s（在整条视频中的起始秒数，从0开始累积）**

## 好文案示例（26字以内，完整句）
✅ "绕线张力差0.1N，线圈寿命少一半" (16字)
✅ "你看这个飞叉转速，比人工快整整5倍" (18字)
✅ "定子槽里铜线排不齐，电机就废了" (16字)
❌ "你看这台绕线机，它的张力传感器能实时反馈，保证每一圈都精准地缠绕到定子上" (30字，太长了)

## 输出 JSON
{{
  "title": "标题 15字内",
  "beats": [
    {{
      "index": 1,
      "text": "口播文案（≤26字，完整句，基于画面写）",
      "visual": "对应画面描述",
      "animation": "zoom|fade|slide|pop|pulse|none",
      "emotion": "hook|curiosity|trust|admire|save",
      "duration_s": 4.0,
      "start_s": 0.0
    }}
  ],
  "outro": {{
    "text": "收藏转发引导",
    "visual": "品牌展示",
    "duration_s": 5.0
  }},
  "total_duration_s": {dur:.0f},
  "bgm_style": "{bgm_style}",
  "tags": ["{tag_str}"]
}}
Return ONLY valid JSON, no markdown. 确保每条text≤26字且是完整句。"""

    try:
        resp = dispatcher.chat([
            {"role": "system", "content": "你是专业短视频脚本编剧。每句口播不超过25字且是完整句。每句必须基于具体的画面内容写，不能用通用套话。输出JSON格式。"},
            {"role": "user", "content": prompt},
        ])
        if not resp:
            return None

        # Parse JSON from response
        import re
        json_match = re.search(r"\{.*\}", resp.content, re.DOTALL)
        if not json_match:
            print(f"  No JSON found in LLM response: {resp.content[:200]}")
            return None

        script = json.loads(json_match.group())

        # Ensure required fields
        if "beats" not in script:
            script["beats"] = []
        if "outro" not in script:
            script["outro"] = {"text": brand.get("outro_template", ""), "visual": "brand logo", "duration_s": 5.0}
        if "metadata" not in script:
            script["metadata"] = {"title": script.get("title", ""), "video_type": "viral_short" if marketing_mode else "content_share"}

        # Scale beat durations to match video duration
        beats_dur = sum(b.get("duration_s", 3) for b in script["beats"])
        outro_dur = script["outro"].get("duration_s", 5)
        total = beats_dur + outro_dur
        target = dur - 1.0  # leave 1s slack
        if abs(total - target) > 1.5 and len(script["beats"]) > 0 and beats_dur > 0:
            scale = (target - outro_dur) / beats_dur
            scale = max(0.5, min(scale, 2.0))  # clamp 0.5x-2x
            for b in script["beats"]:
                b["duration_s"] = round(b.get("duration_s", 3) * scale, 1)
            new_total = sum(b["duration_s"] for b in script["beats"]) + outro_dur
            script["total_duration_s"] = round(new_total, 1)
        else:
            script["total_duration_s"] = round(total, 1)

        # Generate search terms from script
        try:
            terms = generate_terms(script, brand_name, dispatcher)
            if terms:
                script["search_terms"] = terms
                print(f"  Search terms: {chr(44).join(terms[:6])}")
        except Exception as te:
            print(f"  Terms gen: {te}")

        return script

    except Exception as e:
        print(f"  Script generation error: {e}")
        import traceback
        traceback.print_exc()
        return None



def stage3(brand_key="taizhou_longjiang", marketing_mode=False):
    """Stage 3: compose - drawtext + BGM + end frame + encode."""
    print("=" * 60)
    print("Stage 3/3 -- Compose")
    print("=" * 60)

    out_dir = os.path.join(OUTPUT, "stage3")
    os.makedirs(out_dir, exist_ok=True)

    roughcut = os.path.join(OUTPUT, "stage1", "roughcut.mp4")
    script_path = os.path.join(OUTPUT, "stage2", "script.json")
    if not os.path.exists(roughcut) or not os.path.exists(script_path):
        print("  Missing stage1/2 outputs. Run stage1 + stage2 first!")
        return False

    from config.brand_loader import get_brand
    brand = get_brand(brand_key)
    brand_name = brand.get("brand_name", brand_key)

    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    beats = script.get("beats", [])
    outro = script.get("outro", {"text": brand_name, "duration_s": 3.0})
    if not beats:
        print("  No beats in script!")
        return False

    start_times = []
    t = 0.0
    for b in beats:
        start_times.append(t)
        t += b.get("duration_s", 3)
    total_video_dur = t

    # --- [3.0] TTS Narration ---
    narration_audio = None
    narration_srt = None
    print("\n[3.0] Generating TTS narration...")
    try:
        from generators.tts_providers import TTSDispatcher
        tts = TTSDispatcher()
        tts_segments = []
        for i, beat in enumerate(beats):
            txt = beat.get("text", "").strip()
            if txt:
                tts_segments.append({"shot": i + 1, "text": txt})
        if tts_segments:
            result = tts.synthesize_segments(tts_segments, output_dir=out_dir)
            narration_audio = result.audio_path
            narration_srt = result.srt_path
            print(f"  TTS: {len(tts_segments)} segments, {result.total_duration_s:.1f}s total")
            print(f"  SRT: {narration_srt}")
        else:
            print("  No text content, skipping TTS")
    except Exception as e:
        print(f"  TTS FAILED (non-critical): {e}")

    # --- [3.1] 字幕叠加 (drawtext) ---
    text_output = os.path.join(out_dir, "_texted.mp4")
    print("\n[3.1] Adding subtitles...")
    font_path = "C:/Windows/Fonts/msyh.ttc"
    drawtext_filters = []
    for i, (beat, st) in enumerate(zip(beats, start_times)):
        text = beat.get("text", "")
        et = st + beat.get("duration_s", 3)
        enable_expr = "between(t\\," + str(st) + "\\," + str(et) + ")"
        text_quoted = chr(39) + text.replace(chr(39), chr(39)*4) + chr(39)
        f_str = (
            "drawtext=text=" + text_quoted + ":"
            "x=(w-text_w)/2:y=h-th-100:"
            "fontfile='C\\:/Windows/Fonts/msyh.ttc':fontsize=34:fontcolor=white:"
            "box=1:boxcolor=black@0.4:boxborderw=12:"
            "enable=" + chr(39) + enable_expr + chr(39)
        )
        drawtext_filters.append(f_str)
    full_filter = ",".join(drawtext_filters)
    cmd_text = [
        "ffmpeg", "-y", "-i", roughcut,
        "-vf", full_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "main",
        "-colorspace", "bt709",
        "-an", text_output,
    ]
    r = run_ff(cmd_text, timeout=600)
    if r.returncode != 0:
        print(f"  Drawtext FAILED: {r.stderr[-300:]}")
        return False
    print(f"  Subtitles done: {os.path.getsize(text_output)//1024}KB")

    # --- [3.1a] HyperFrames 动画叠层 (GSAP动效/扫光/角标) ---
    current_video = text_output
    try:
        from generators.hyperframe_layer import generate as hf_generate, render_to_video as hf_render
        hf_html = hf_generate(script_path, out_dir)
        hf_video = os.path.join(out_dir, "_overlay_raw.mp4")
        hf_result = hf_render(hf_html, hf_video, total_video_dur + outro.get("duration_s", 3))
        if hf_result and os.path.exists(hf_result) and os.path.getsize(hf_result) > 10000:
            hf_composited = os.path.join(out_dir, "_with_overlay.mp4")
            cmd_overlay = [
                "ffmpeg", "-y",
                "-i", current_video,
                "-i", hf_result,
                "-filter_complex",
                "[1:v]chromakey=color=#00ff00:similarity=0.15:blend=0.1[over];[0:v][over]overlay[outv]",
                "-map", "[outv]",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-pix_fmt", "yuv420p",
                "-an", hf_composited,
            ]
            r = run_ff(cmd_overlay, timeout=300)
            if r.returncode == 0:
                current_video = hf_composited
                print(f"  [OK] HyperFrames overlay composited: {os.path.getsize(hf_composited)//1024}KB")
            else:
                print(f"  Overlay composite FAILED (non-critical): {r.stderr[-150:]}")
        else:
            print("  HyperFrames overlay empty, skipping")
    except Exception as hf_overlay_err:
        print(f"  HyperFrames overlay SKIPPED ({hf_overlay_err})")

    print("\n[3.2] Adding TTS narration + BGM (Ducking)...")
    bgm_path = os.path.join(ROOT, "assets", "bgm", "corporate_tech.mp3")
    bgm_output = os.path.join(out_dir, "_with_bgm.mp4")
    if os.path.exists(bgm_path) and os.path.getsize(bgm_path) > 1000:
        dur_total = total_video_dur + outro.get("duration_s", 3)
        if narration_audio and os.path.exists(narration_audio):
            cmd_bgm = [
                "ffmpeg", "-y",
                "-i", current_video,
                "-i", bgm_path,
                "-i", narration_audio,
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "128k",
                "-map", "0:v:0",
                "-filter_complex",
                f"[1:a]volume=0.12,afade=t=out:st={dur_total-2}:d=2[bgm];"
                f"[2:a]volume=1.0,afade=t=out:st={dur_total-1}:d=1[voice];"
                f"[bgm][voice]sidechaincompress=threshold=0.025:ratio=6:attack=5:release=200:level_sc=1[outa]",
                "-map", "[outa]",
                "-t", str(dur_total),
                bgm_output,
            ]
            r = run_ff(cmd_bgm, timeout=300)
            if r.returncode != 0:
                print(f"  BGM FAILED: {r.stderr[-200:]}")
                import shutil
                shutil.copy2(current_video, bgm_output)
        else:
            cmd_bgm = [
                "ffmpeg", "-y",
                "-i", current_video,
                "-i", bgm_path,
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "128k",
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest",
                "-af", f"volume=0.5,afade=t=out:st={dur_total-2}:d=2",
                bgm_output,
            ]
            r = run_ff(cmd_bgm, timeout=300)
            if r.returncode != 0:
                print(f"  BGM FAILED: {r.stderr[-200:]}")
                import shutil
                shutil.copy2(current_video, bgm_output)
    else:
        import shutil
        shutil.copy2(current_video, bgm_output)
    print(f"  BGM done: {os.path.getsize(bgm_output)//1024}KB")

    print("\n[3.2a] Adding SFX cues...")
    sfx_dir = os.path.join(ROOT, "assets", "sfx")
    sfx_map = {
        "zoom": "whoosh_01", "fade": "whoosh_02", "slide": "whoosh_02",
        "pop": "impact_01", "pulse": "impact_02", "hook": "ping_01",
        "curiosity": "ding_01", "surprise": "impact_01", "trust": "impact_02",
        "desire": "impact_01", "action": "impact_01",
    }
    sfx_inputs = []
    sfx_mix_parts = []
    for i, (beat, st) in enumerate(zip(beats, start_times)):
        anim = beat.get("animation", "")
        sfx_id = sfx_map.get(anim, "")
        if not sfx_id:
            continue
        sfx_path = os.path.join(sfx_dir, f"{sfx_id}.mp3")
        if not os.path.exists(sfx_path) or os.path.getsize(sfx_path) < 100:
            continue
        sfx_inputs.extend(["-i", sfx_path])
        vol = beat.get("emotion", "") in ("action", "desire") and 0.5 or 0.3
        delay_ms = int(st * 1000)
        sfx_mix_parts.append(
            f"[{len(sfx_mix_parts)+1}:a]adelay={delay_ms}|{delay_ms},volume={vol}[s{i}]"
        )
    if sfx_mix_parts:
        sfx_output = os.path.join(out_dir, "_with_sfx.mp4")
        all_mix = "".join(f"[s{j}]" for j in range(len(sfx_mix_parts)))
        bgm_label = "[0:a]" if sfx_inputs else ""
        mix_inputs = bgm_label + all_mix
        n_inputs = 1 + len(sfx_mix_parts)
        mix_filter = ";".join(sfx_mix_parts) + f";{mix_inputs}amix=inputs={n_inputs}:duration=first:dropout_transition=2[a];[a]loudnorm=I=-16:LRA=7:TP=-1.5"
        cmd_sfx = ["ffmpeg", "-y", "-i", bgm_output] + sfx_inputs + [
            "-filter_complex", mix_filter,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-shortest",
            sfx_output]
        r = run_ff(cmd_sfx, timeout=300)
        if r.returncode == 0:
            bgm_output = sfx_output
            print(f"  SFX added: {len(sfx_mix_parts)} cues")
        else:
            print(f"  SFX FAILED (non-critical): {r.stderr[-150:]}")
    else:
        print("  No SFX cues to add")

    print("\n[3.3] Adding end frame...")
    end_frame_video = os.path.join(out_dir, "_end_frame.mp4")
    end_dur = outro.get("duration_s", 3)
    # Simple end frame with one drawtext call (no escaped commas)
    cmd_end = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0057b8:s=1920x1080:d=%d:r=30" % end_dur,
        "-vf", f"drawtext=text='{outro.get(chr(34)+"text"+chr(34), brand_name)}':fontfile='C\\:/Windows/Fonts/msyh.ttc':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-th)/2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an", end_frame_video,
    ]
    r = run_ff(cmd_end, timeout=120)
    if r.returncode != 0:
        print("  End frame FAILED: " + r.stderr[-200:])
        return False
    print("  End frame done: %dKB" % (os.path.getsize(end_frame_video)//1024))
    print("\n[3.4] Concatenating + final encode...")
    final_output = os.path.join(out_dir, "final.mp4")
    concat_file = os.path.join(out_dir, "_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(bgm_output).replace(chr(39), chr(39)*4)}'\n")
        f.write(f"file '{os.path.abspath(end_frame_video).replace(chr(39), chr(39)*4)}'\n")

    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        final_output,
    ]
    r = run_ff(cmd_concat, timeout=120)
    if r.returncode != 0:
        print(f"  Concat FAILED: {r.stderr[-300:]}")
        return False

    print(f"  Final output: {final_output}")
    print(f"  Size: {os.path.getsize(final_output)//1024}KB")

    # --- [3.5] Generate publish plan ---
    print("\n[3.5] Generating publish plan...")
    try:
        from generators.publish_planner import generate as gen_publish
        publish_plan = gen_publish(script_path, brand)
        publish_path = os.path.join(OUTPUT, "stage3", "publish_plan.json")
        with open(publish_path, "w", encoding="utf-8") as f:
            json.dump(publish_plan, f, ensure_ascii=False, indent=2)
        print(f"  Publish plan saved: {publish_path}")
        for pname, pinfo in publish_plan["platforms"].items():
            print(f"    {pname:12s} | {pinfo['title'][:25]:25s} | {pinfo['best_time'][0]}")
    except Exception as e:
        print(f"  Publish plan FAILED (non-critical): {e}")

    print("\n" + "=" * 60)
    print("Run audit: audit_compose.py")
    print("=" * 60)
    audit_ok = run_audit(
        os.path.join(ROOT, "auditors", "audit_compose.py"),
        final_output, script_path
    )
    if audit_ok:
        print("\nStage 3 PASS -- audit 5/5")
        return True
    else:
        print("\nStage 3 FAIL -- audit rejected")
        return False




# ====== CLI Entry Point ======


def stage0(footage_pattern, brand_key="taizhou_longjiang"):
    """Stage 0:???? - ?ffprobe????,??????."""
    print("=" * 60)
    print("Stage 0/3 -- ????")
    print("=" * 60)
    
    video_files = sorted(glob.glob(footage_pattern))
    if not video_files:
        print("  No footage: " + footage_pattern)
        return False
    
    print("  Found %d files\n" % len(video_files))
    for vf in video_files:
        dur = ffprobe_get(vf, "duration") or "?"
        pix = ffprobe_get(vf, "pix_fmt", "stream") or "?"
        codec = ffprobe_get(vf, "codec_name", "stream") or "?"
        w = ffprobe_get(vf, "width", "stream") or "?"
        hv = ffprobe_get(vf, "height", "stream") or "?"
        smb = os.path.getsize(vf) / 1024 / 1024
        hdr = "HDR(HLG)" if detect_hdr(vf) else "SDR"
        name = Path(vf).name
        print("  [%s]" % name)
        print("    Duration: %.1fs | %.1fMB | %s" % (float(dur) if dur.replace(".","").isdigit() else 0, smb, codec))
        print("    Resolution: %sx%s | %s | %s" % (w, hv, pix, hdr))
        print()
    
    print("??????.")
    return True




# ====== Status Auto-Update ======

def update_status(stage, result):
    """Auto-update STATUS.md after each stage run."""
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Gather outputs
    stage1_mp4 = os.path.join(OUTPUT, "stage1", "roughcut.mp4")
    stage2_json = os.path.join(OUTPUT, "stage2", "script.json")
    stage3_mp4 = os.path.join(OUTPUT, "stage3", "final.mp4")
    
    s1_info = "-"
    if os.path.exists(stage1_mp4):
        dur = ffprobe_get(stage1_mp4, "duration") or "?"
        sz = os.path.getsize(stage1_mp4) / 1024
        s1_info = f"{float(dur):.1f}s/{sz:.0f}KB" if dur != "?" else "?"
    
    s2_info = "-"
    if os.path.exists(stage2_json):
        import json
        with open(stage2_json, "r", encoding="utf-8") as f:
            s2 = json.load(f)
        s2_info = f"{len(s2.get("beats", []))} beats"
    
    s3_info = "-"
    if os.path.exists(stage3_mp4):
        dur = ffprobe_get(stage3_mp4, "duration") or "?"
        sz = os.path.getsize(stage3_mp4) / 1024
        s3_info = f"{float(dur):.1f}s/{sz:.0f}KB" if dur != "?" else "?"
    
    status = f"""# Auto Video Platform — \u5b9e\u65f6\u72b6\u6001
> \u81ea\u52a8\u66f4\u65b0 | \u6700\u540e\u66f4\u65b0: {now}

## \u7ba1\u7ebf\u72b6\u6001

| \u9636\u6bb5 | \u6700\u540e\u8fd0\u884c | \u5ba1\u8ba1 | \u4ea7\u51fa |
|------|----------|------|------|
| Stage 1 \u7c97\u526a | {"✅" if os.path.exists(stage1_mp4) else "❌"} {now if os.path.exists(stage1_mp4) else "-"} | {"5/5 PASS" if os.path.exists(os.path.join(OUTPUT, "stage1", "AUDIT_PASS.txt")) else "-"} | {s1_info} |
| Stage 2 \u811a\u672c | {"✅" if os.path.exists(stage2_json) else "❌"} {now if os.path.exists(stage2_json) else "-"} | {"5/5 PASS" if os.path.exists(os.path.join(OUTPUT, "stage2", "AUDIT_PASS.txt")) else "-"} | {s2_info} |
| Stage 3 \u5408\u6210 | {"✅" if os.path.exists(stage3_mp4) else "❌"} {now if os.path.exists(stage3_mp4) else "-"} | {"5/5 PASS" if os.path.exists(os.path.join(OUTPUT, "stage3", "AUDIT_PASS.txt")) else "-"} | {s3_info} |
"""
    
    status_path = os.path.join(ROOT, "STATUS.md")
    try:
        with open(status_path, "w", encoding="utf-8") as f:
            f.write(status)
    except:
        pass  # Best effort

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto Video Platform Pipeline")
    parser.add_argument("stage", choices=["0","1","2","3","stage0","stage1","stage2","stage3"],
                        help="Pipeline stage to run")
    parser.add_argument("footage", nargs="?",
                        default="D:/隆江视频素材/IMG_034*.MP4",
                        help="Footage glob pattern (for stage1)")
    parser.add_argument("--brand", default="taizhou_longjiang",
                        help="Brand key (default: taizhou_longjiang)")
    parser.add_argument("--marketing-mode", "-m", action="store_true",
                        help="Generate marketing script with CTA (default: content-only)")
    
    args = parser.parse_args()
    s = args.stage.replace("stage", "")
    
    if s == "0":
        success = stage0(args.footage, args.brand)
    elif s == "1":
        success = stage1(args.footage, args.brand)
    elif s == "2":
        success = stage2(args.brand, args.marketing_mode)
    elif s == "3":
        success = stage3(args.brand, args.marketing_mode)
    else:
        print("Unknown stage: " + args.stage)
        success = False
    
    update_status("all", success)
sys.exit(0 if success else 1)










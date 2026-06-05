"""
HyperFrames 动画层生成器
为实拍素材叠加 GSAP 动效字幕 + HUD 扫光 + 脉冲标注
输入: script.json
输出: overlay.html → Chromium 渲染 → overlay.mp4 (绿幕) → 合成到 roughcut
"""

import json, os, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GSAP_SRC = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"

# ── beat animation → CSS class mapping ──
ANIM_CLASSES = {
    "zoom":   "anim-zoom",
    "fade":   "anim-fade",
    "slide":  "anim-slide",
    "pop":    "anim-pop",
    "pulse":  "anim-pulse",
}

def generate(script_path: str, output_dir: str) -> str:
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    beats = script.get("beats", [])
    outro = script.get("outro", {})
    total_dur = script.get("total_duration_s", 30) + outro.get("duration_s", 3)

    # ── Build beat HTML blocks ──
    beat_html = ""
    gsap_timeline = ""
    bg_color = "#06060b"

    for i, b in enumerate(beats):
        text = b.get("text", "")
        anim = b.get("animation", "fade")
        emotion = b.get("emotion", "neutral")
        st = b.get("start_s", 0)
        dur = b.get("duration_s", 3)
        anim_class = ANIM_CLASSES.get(anim, "anim-fade")

        # Color based on emotion
        color_map = {
            "hook": "#FFD700", "curiosity": "#00E5FF",
            "trust": "#00E676", "admire": "#FF9100",
            "save": "#FF4081", "pain": "#FF1744",
            "solution": "#00E676", "proof": "#448AFF",
            "action": "#FFD700", "neutral": "#FFFFFF",
        }
        accent = color_map.get(emotion, "#FFFFFF")

        # GSAP opacity = fade in/out within beat window
        gsap_timeline += f"""
  tl.to("#b{i}", {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, {st});
  tl.to("#b{i}", {{ opacity: 0, duration: 0.4, ease: "power2.in" }}, {st + dur - 0.4});"""

        # If zoom, add scale
        if anim == "zoom":
            gsap_timeline += f"""
  tl.fromTo("#b{i}", {{ scale: 0.85, transformOrigin: "center center" }}, {{ scale: 1, duration: {dur}, ease: "power2.out" }}, {st});"""

        # If pop, add y bounce
        if anim == "pop":
            gsap_timeline += f"""
  tl.fromTo("#b{i}", {{ y: 40 }}, {{ y: 0, duration: 0.5, ease: "back.out(1.7)" }}, {st});"""

        # If slide, add x shift
        if anim == "slide":
            gsap_timeline += f"""
  tl.fromTo("#b{i}", {{ x: -60 }}, {{ x: 0, duration: 0.5, ease: "power2.out" }}, {st});"""

        # HUD scan line for this beat
        gsap_timeline += f"""
  tl.fromTo("#scan-{i}", {{ scaleY: 0, transformOrigin: "top center" }}, {{ scaleY: 1, duration: 0.3, ease: "power2.out" }}, {st});
  tl.to("#scan-{i}", {{ scaleY: 0, duration: 0.3, ease: "power2.in" }}, {st + dur - 0.3});"""

        # Corner brackets for emphasis
        if emotion in ("hook", "proof", "save"):
            gsap_timeline += f"""
  tl.fromTo("#br-{i}", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }}, {st + 0.2});
  tl.to("#br-{i}", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {st + dur - 0.3});"""

        beat_html += f"""
  <div class="beat-wrapper" id="bw{i}" style="display:none" data-start="{st}" data-end="{st + dur}">
    <div class="scan-line" id="scan-{i}"></div>
    <div class="corner-brackets" id="br-{i}">
      <div class="cb-tl"></div><div class="cb-tr"></div>
      <div class="cb-bl"></div><div class="cb-br"></div>
    </div>
    <div class="beat-text {anim_class}" id="b{i}" style="color:{accent}">{text}</div>
  </div>"""

    # ── Assemble HTML ──
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<script src="{GSAP_SRC}"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:{bg_color};font-family:"Microsoft YaHei","PingFang SC",sans-serif}}

/* Green screen for chroma key — whole page is green, only animated elements appear */
body{{background:#00ff00}}
.beat-wrapper{{position:absolute;inset:0;pointer-events:none}}

/* Scan line — top HUD bar */
.scan-line{{position:absolute;top:0;left:0;width:1080px;height:3px;background:linear-gradient(90deg,transparent,#00e5ff80,transparent);transform-origin:top center}}

/* Text styling */
.beat-text{{position:absolute;bottom:180px;left:60px;right:60px;text-align:center;font-size:38px;font-weight:700;color:#fff;text-shadow:0 2px 20px rgba(0,0,0,0.9);line-height:1.4;opacity:0}}
.anim-zoom{{transform-origin:center center}}
.anim-pop{{transform-origin:center bottom}}
.anim-slide{{transform-origin:left center}}

/* Corner brackets */
.corner-brackets{{position:absolute;inset:30px;opacity:0}}
.cb-tl{{position:absolute;top:0;left:0;width:40px;height:40px;border-top:2px solid #00e5ff80;border-left:2px solid #00e5ff80}}
.cb-tr{{position:absolute;top:0;right:0;width:40px;height:40px;border-top:2px solid #00e5ff80;border-right:2px solid #00e5ff80}}
.cb-bl{{position:absolute;bottom:0;left:0;width:40px;height:40px;border-bottom:2px solid #00e5ff80;border-left:2px solid #00e5ff80}}
.cb-br{{position:absolute;bottom:0;right:0;width:40px;height:40px;border-bottom:2px solid #00e5ff80;border-right:2px solid #00e5ff80}}

/* Tech HUD grid overlay */
.hud-grid{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 40px,rgba(0,229,255,0.03) 40px,rgba(0,229,255,0.03) 41px);pointer-events:none;opacity:0.5}}
</style>
</head>
<body>
<div class="hud-grid"></div>
{beat_html}
<script>
window.addEventListener("DOMContentLoaded", function(){{
  var tl = gsap.timeline({{paused:true}});
{gsap_timeline}
  window.__timelines = window.__timelines || {{}};
  window.__timelines["overlay"] = tl;
  tl.play();
}});
</script>
</body>
</html>"""

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "overlay.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def render_to_video(html_path: str, output_path: str, duration: float):
    """Render HTML overlay to MP4 via Playwright video recording + ffmpeg."""
    import time, glob

    html_path = os.path.abspath(html_path)
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    out_dir = os.path.dirname(output_path)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu"])
        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            record_video_dir=out_dir,
            record_video_size={"width": 1080, "height": 1920},
        )
        page = context.new_page()
        page.goto(file_url, wait_until="networkidle")
        time.sleep(0.5)  # let GSAP initialize
        page.wait_for_timeout(int(duration * 1000) + 500)  # wait for full duration
        context.close()
        browser.close()

    # Playwright saves video as .webm in out_dir
    webm_files = sorted(glob.glob(os.path.join(out_dir, "*.webm")))
    if not webm_files:
        print("  Playwright video recording produced no file, skipping overlay")
        return None

    webm_path = webm_files[-1]
    # Convert webm to mp4 with green bg for chroma key
    mp4_path = output_path
    subprocess.run([
        "ffmpeg", "-y",
        "-i", webm_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-vf", "setdar=9:16",
        mp4_path
    ], check=True, capture_output=True)
    os.remove(webm_path)  # cleanup
    size_kb = os.path.getsize(mp4_path) // 1024
    print(f"  Overlay video: {mp4_path} ({size_kb}KB)")
    return mp4_path

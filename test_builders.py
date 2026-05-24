"""End-to-end integration test for the builders layer.

Exercises: CompositionBuilder → all 8 components → HTML output → validation.
"""
import sys, os

# Ensure platform root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from builders import CompositionBuilder, StoryboardConfig, SubtitleEngine

# ---------------------------------------------------------------------------
# 1. Build a complete storyboard for an "AI照妖镜" episode
# ---------------------------------------------------------------------------

storyboard_dict = {
    "scenes": [
        # ── S0: Social media frame (hook: "这张朋友圈照片看起来正常对吧?") ──
        {
            "component": "social-frame",
            "start": 0.0,
            "duration": 4.0,
            "config": {
                "username": "小美",
                "avatar_letter": "美",
                "post_text": "姐妹聚会太开心啦！🎉✨",
                "post_time": "3小时前",
                "img_src": "assets/img2_group_photo.png",
                "likes": "128",
                "comments": [
                    ("小花", "好美啊！在哪里拍的？"),
                    ("大明", "下次带我一起！"),
                    ("小美 回复 小花", "就在城西那家新开的店~"),
                ],
            },
        },

        # ── S0→S1: Glitch transition ──
        {
            "component": "glitch-transition",
            "start": 3.5,
            "duration": 2.0,
            "config": {},
        },

        # ── S1: Reveal — "它不是真人拍的。是AI生成的。" ──
        {
            "component": "reveal-text",
            "start": 5.5,
            "duration": 3.0,
            "config": {
                "reveal_text": "它不是真人拍的。<br/>是AI生成的。",
                "anticipation_text": "来，我放大三个细节给你看 ↓",
                "img_src": "assets/img2_group_photo.png",
            },
        },

        # ── S2: Zoom-analyze — hand flaw (6 fingers) ──
        {
            "component": "zoom-analyze",
            "start": 8.0,
            "duration": 8.0,
            "config": {
                "label": "① 先看手",
                "img_id": "img2",
                "img_src": "assets/img2_group_photo.png",
                "zoom_origin_x": 540,
                "zoom_origin_y": 1200,
                "zoom_scale": 2.6,
                "keyword_text": "6根手指",
                "keyword_color": "#ff1744",
                "keyword_top": 760,
                "keyword_left": 100,
                "keyword_id": "kw2",
                "keyword_delay": 2.0,
                "label_id": "lbl2",
                "markers": [
                    {"id": "mk2a", "x": 480, "y": 1200, "w": 120, "h": 120, "delay": 2.0},
                    {"id": "mk2b", "x": 620, "y": 1180, "w": 100, "h": 100, "delay": 2.8},
                ],
                "data_badge": {"top": 700, "right": 70, "big": "6", "sub": "根手指"},
                "data_id": "dv2",
                "data_delay": 3.5,
                "reference_lines": [],
                "count_badge": {"top": 1020, "right": 80, "value": "1"},
                "count_id": "cb2",
                "count_delay": 4.0,
                "zoom_out_at": 7.0,
            },
        },

        # ── S3: Zoom-analyze — face asymmetry ──
        {
            "component": "zoom-analyze",
            "start": 16.0,
            "duration": 8.0,
            "config": {
                "label": "② 再看脸",
                "img_id": "img3",
                "img_src": "assets/img2_group_photo.png",
                "zoom_origin_x": 600,
                "zoom_origin_y": 500,
                "zoom_scale": 3.0,
                "keyword_text": "五官歪斜",
                "keyword_color": "#ff9100",
                "keyword_top": 760,
                "keyword_left": 100,
                "keyword_id": "kw3",
                "keyword_delay": 2.0,
                "label_id": "lbl3",
                "markers": [
                    {"id": "mk3a", "x": 540, "y": 440, "w": 200, "h": 260, "delay": 2.0},
                    {"id": "mk3b", "x": 700, "y": 380, "w": 90, "h": 90, "delay": 2.8},
                    {"id": "mk3c", "x": 380, "y": 420, "w": 90, "h": 90, "delay": 3.6},
                ],
                "data_badge": {"top": 700, "right": 70, "big": "±12°", "sub": "角度偏差"},
                "data_id": "dv3",
                "data_delay": 4.0,
                "reference_lines": [
                    {"id": "rl3a", "type": "ref", "top": 440, "left": 0, "width": 1080, "delay": 3.0},
                    {"id": "rl3b", "type": "deviation", "top": 460, "left": 100, "width": 880, "delay": 3.3},
                ],
                "count_badge": {"top": 1020, "right": 80, "value": "2"},
                "count_id": "cb3",
                "count_delay": 5.0,
                "zoom_out_at": 7.0,
            },
        },

        # ── S4: Zoom-analyze — joint straight line ──
        {
            "component": "zoom-analyze",
            "start": 24.0,
            "duration": 8.0,
            "config": {
                "label": "③ 看关节",
                "img_id": "img4",
                "img_src": "assets/img2_group_photo.png",
                "zoom_origin_x": 500,
                "zoom_origin_y": 1400,
                "zoom_scale": 2.8,
                "keyword_text": "关节僵直",
                "keyword_color": "#ff1744",
                "keyword_top": 760,
                "keyword_left": 100,
                "keyword_id": "kw4",
                "keyword_delay": 2.0,
                "label_id": "lbl4",
                "markers": [
                    {"id": "mk4a", "x": 440, "y": 1400, "w": 110, "h": 110, "delay": 2.0},
                    {"id": "mk4b", "x": 560, "y": 1420, "w": 110, "h": 110, "delay": 2.8},
                ],
                "data_badge": {"top": 700, "right": 70, "big": "0°", "sub": "弯曲角度"},
                "data_id": "dv4",
                "data_delay": 3.5,
                "reference_lines": [
                    {"id": "rl4a", "type": "joint-straight-line", "top": 1410, "left": 400, "width": 200, "delay": 3.0},
                ],
                "count_badge": {"top": 1020, "right": 80, "value": "3"},
                "count_id": "cb4",
                "count_delay": 4.5,
                "zoom_out_at": 7.0,
            },
        },

        # ── S5: Compare split — AI vs Real ──
        {
            "component": "compare-split",
            "start": 32.0,
            "duration": 10.0,
            "config": {
                "ai_img": "assets/img2_group_photo.png",
                "real_img": "assets/real_group_generated.png",
                "checks": [
                    {"label": "手指数量", "fail": "✗ 6根", "pass": "✓ 5根"},
                    {"label": "五官对称", "fail": "✗ 歪了", "pass": "✓ 对称"},
                    {"label": "关节弯曲", "fail": "✗ 僵直", "pass": "✓ 自然"},
                ],
                "summary_text": "记住查三处：手 · 脸 · 关节",
            },
        },

        # ── S6: Outro ──
        {
            "component": "outro",
            "start": 42.0,
            "duration": 10.0,
            "config": {
                "title": "AI照妖镜",
                "subtitle": "关注我，下次被骗的不是你",
                "teaser": "下期：5个AI检测工具横评 →",
                "logo_char": "鉴",
            },
        },
    ],
    "audio_src": "assets/narration.mp3",
    "bgm_src": "assets/bgm_tech.mp3",
    "global_overlays": {
        "scan_show_at": 8.0,
        "scan_hide_at": 42.0,
        "progress_segments": [
            {"start": 5.5},
            {"start": 16.0},
            {"start": 24.0},
            {"start": 32.0},
            {"start": 42.0},
        ],
    },
    "metadata": {
        "title": "AI照妖镜 · 第1期 · 朋友圈照片破绽",
        "author": "auto-video-platform",
        "episode": 1,
    },
}

# ---------------------------------------------------------------------------
# 2. Build
# ---------------------------------------------------------------------------

print("=" * 60)
print("Building complete HyperFrames HTML from storyboard...")
print("=" * 60)

builder = CompositionBuilder()
html = builder.build_from_dict(storyboard_dict)

# ---------------------------------------------------------------------------
# 3. Validate
# ---------------------------------------------------------------------------

print(f"\nHTML output: {len(html):,} chars")
print(f"Scenes: {len(storyboard_dict['scenes'])}")

checks = {
    "DOCTYPE": "<!doctype html>" in html,
    "gsap script": "gsap.min.js" in html,
    "window.__timelines": "window.__timelines" in html,
    "tl.play()": "tl.play()" in html,
    "narration audio": "narration" in html,
    "bgm audio": "bgm_tech" in html,
    "scan overlay": "scanOverlay" in html,
    "progress bar": "progressFill" in html,
    "social frame": "smBg" in html,
    "glitch transition": "glR" in html,
    "reveal text": "revealTxt" in html,
    "zoom analyze S2": "img2" in html and "kw2" in html,
    "zoom analyze S3": "img3" in html and "kw3" in html,
    "zoom analyze S4": "img4" in html and "kw4" in html,
    "compare split": "cmpAI" in html and "cmpReal" in html,
    "outro": "otitle" in html,
    "neon markers S2": "mk2a" in html and "mk2b" in html,
    "neon markers S3": "mk3a" in html and "mk3b" in html and "mk3c" in html,
    "reference lines S3": "rl3a" in html and "rl3b" in html,
    "joint line S4": "rl4a" in html,
    "count badges": "cb2" in html and "cb4" in html,
    "data badges": "dv2" in html and "dv4" in html,
    "checklist rows": "chk1" in html and "chk2" in html and "chk3" in html,
    "zoom animation": "power3.inOut" in html,
    "back.out easing": "back.out(2)" in html,
}

all_pass = True
for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_pass = False
    print(f"  [{status}] {name}")

print(f"\n{'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")

# ---------------------------------------------------------------------------
# 4. Extract SFX + subtitles for verification
# ---------------------------------------------------------------------------

sb = StoryboardConfig(
    scenes=storyboard_dict["scenes"],
    audio_src=storyboard_dict["audio_src"],
    bgm_src=storyboard_dict["bgm_src"],
    global_overlays=storyboard_dict["global_overlays"],
    metadata=storyboard_dict["metadata"],
)
sfx = builder.extract_sfx(sb)
print(f"\nSFX triggers: {len(sfx)}")
for t in sfx:
    print(f"  {t.sfx_id} @ {t.at_time:.2f}s (vol={t.volume})")

# ---------------------------------------------------------------------------
# 5. Write output
# ---------------------------------------------------------------------------

output_path = os.path.join(os.path.dirname(__file__), "test_output.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\nOutput written to: {output_path}")
print("Done!")

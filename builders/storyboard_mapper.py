"""StoryboardMapper — ScriptGenerator output → CompositionBuilder component configs.

Bridges the gap between the ScriptGenerator's generic storyboard (narrative
shots with visual/audio/caption) and the CompositionBuilder's component-specific
config (social-frame, zoom-analyze with marker positions, etc.).

For each video type, a mapping profile defines how generic shots map to
components and how timing/config is derived from the script + analysis data.

Usage:
    from builders.storyboard_mapper import StoryboardMapper
    mapper = StoryboardMapper()
    component_storyboard = mapper.map(script, analysis_report, tts_timeline)
    html = builder.build_from_dict(component_storyboard)
"""

import os
from dataclasses import dataclass, field
from typing import Optional


def _brand_name() -> str:
    try:
        from config.brand_loader import get_brand_name
        return get_brand_name()
    except Exception:
        return "Auto Video"


# ---------------------------------------------------------------------------
# Mapping profiles — one per video type
# ---------------------------------------------------------------------------

@dataclass
class ShotMapping:
    """How one generic storyboard shot maps to a component."""
    component: str                    # component name, e.g. "zoom-analyze"
    config_template: dict = field(default_factory=dict)  # static config defaults
    # Dynamic config keys to extract from the shot or findings:
    config_from_shot: list[str] = field(default_factory=list)
    config_from_finding: list[str] = field(default_factory=list)


# Profile for "ai-flaw-detect" video type
AI_FLAW_DETECT_PROFILE: list[ShotMapping] = [
    # Shot 0: Hook → social-frame (朋友圈伪装)
    ShotMapping(
        component="social-frame",
        config_template={
            "username": "小美",
            "avatar_letter": "美",
            "post_time": "2小时前",
            "likes": "156",
            "comments": [
                ("小芳", "在哪里拍的？好好看！"),
                ("阿杰", "这是AI生成的吧？有点假"),
                ("小美 回复 阿杰", "怎么可能~"),
            ],
        },
        config_from_shot=["post_text", "img_src"],
    ),
    # Transition: glitch
    ShotMapping(
        component="glitch-transition",
        config_template={},
    ),
    # Reveal: "它不是真人拍的。是AI生成的。"
    ShotMapping(
        component="reveal-text",
        config_template={
            "reveal_text": "它不是真人拍的。<br/>是AI生成的。",
            "anticipation_text": "来，我放大三个细节给你看 ↓",
        },
        config_from_shot=["img_src"],
    ),
    # Flaw zoom shots (one per finding) — repeated for each flaw
    ShotMapping(
        component="zoom-analyze",
        config_template={
            "zoom_scale": 2.6,
            "keyword_color": "#ff1744",
            "keyword_top": 760,
            "keyword_left": 100,
        },
        config_from_shot=["img_src"],
        config_from_finding=["label", "keyword_text", "markers", "data_badge"],
    ),
    # Compare split
    ShotMapping(
        component="compare-split",
        config_template={
            "checks": [
                {"label": "手指数量", "fail": "✗ 异常", "pass": "✓ 正常"},
                {"label": "五官对称", "fail": "✗ 歪斜", "pass": "✓ 对称"},
                {"label": "关节弯曲", "fail": "✗ 僵直", "pass": "✓ 自然"},
            ],
            "summary_text": "记住查三处：手 · 脸 · 关节",
        },
        config_from_shot=["ai_img", "real_img"],
    ),
    # Outro
    ShotMapping(
        component="outro",
        config_template={
            "title": _brand_name(),
            "subtitle": "关注我，下次被骗的不是你",
            "teaser": "下期见 →",
            "logo_char": "鉴",
        },
        config_from_shot=["title", "subtitle", "teaser"],
    ),
]


# ---------------------------------------------------------------------------
# Mapper
# ---------------------------------------------------------------------------

class StoryboardMapper:
    """Convert ScriptGenerator output → Component storyboard for CompositionBuilder."""

    def __init__(self, video_type: str = "ai-flaw-detect"):
        self.video_type = video_type
        self._profile = self._load_profile(video_type)

    # ─── Public API ──────────────────────────────────────────

    def map(self, script: dict, analysis_report: dict,
            tts_timeline=None, audio_src: str = "",
            bgm_src: str = "") -> dict:
        """Main entry: script + analysis → component storyboard dict.

        Args:
            script: ScriptGenerator output (with storyboard, hook, etc.)
            analysis_report: AssetAnalyzer output (with flaw positions)
            tts_timeline: Optional TTSTimeline for accurate audio timing
            audio_src: Path to narration audio file
            bgm_src: Path to background music file

        Returns:
            dict suitable for CompositionBuilder.build_from_dict()
        """
        storyboard = script.get("storyboard", [])
        findings = self._extract_findings(analysis_report)
        images = self._extract_images(analysis_report)
        primary_img = images[0] if images else "assets/img2_group_photo.png"
        real_img = self._pick_real_image(analysis_report, primary_img)

        # Calculate timing
        if tts_timeline and tts_timeline.segments:
            timing = self._timing_from_tts(tts_timeline)
        else:
            timing = self._timing_from_durations(storyboard)

        # Map shots to components
        scenes = self._map_shots(storyboard, findings, primary_img, real_img, timing)

        # Build global overlays config
        total_dur = max(s["start"] + s["duration"] for s in scenes) if scenes else 52
        analysis_start = next(
            (s["start"] for s in scenes if s["component"] == "zoom-analyze"), 8.0
        )
        analysis_end = next(
            (s["start"] + s["duration"] for s in reversed(scenes)
             if s["component"] == "zoom-analyze"), total_dur - 10
        )

        return {
            "scenes": scenes,
            "audio_src": audio_src or (tts_timeline.audio_path if tts_timeline else ""),
            "bgm_src": bgm_src,
            "global_overlays": {
                "scan_show_at": analysis_start,
                "scan_hide_at": analysis_end,
                "progress_segments": self._progress_segments(scenes, total_dur),
            },
            "metadata": {
                "title": script.get("titles", [{}])[0].get("text", "") if script.get("titles") else "",
                "author": "auto-video-platform",
                "video_type": self.video_type,
            },
        }

    # ─── Timing ──────────────────────────────────────────────

    def _timing_from_tts(self, tts_timeline) -> list[dict]:
        """Calculate absolute start times from TTS segment durations."""
        times = []
        cursor = 0.0
        pause = 0.35
        for seg in tts_timeline.segments:
            times.append({"start": cursor, "duration": seg.duration_s})
            cursor += seg.duration_s + pause
        return times

    def _timing_from_durations(self, storyboard: list[dict]) -> list[dict]:
        """Fallback: parse duration strings like '5s', '10s'."""
        times = []
        cursor = 0.0
        for shot in storyboard:
            dur_str = shot.get("duration", "5s")
            try:
                dur = float(dur_str.replace("s", ""))
            except (ValueError, AttributeError):
                dur = 5.0
            times.append({"start": cursor, "duration": dur})
            cursor += dur
        return times

    # ─── Shot mapping ────────────────────────────────────────

    def _map_shots(self, storyboard: list[dict], findings: list[dict],
                   primary_img: str, real_img: str, timing: list[dict]) -> list[dict]:
        """Map generic storyboard shots → component scenes with configs.

        For ai-flaw-detect, the structure is always:
          social-frame → glitch-transition → reveal-text →
          N× zoom-analyze → compare-split → outro
        """
        scenes = []
        theme = self._detect_episode_theme(findings)
        flaw_findings = [f for f in findings
                         if f.get("detector") in ("face", "hand", "text", "texture")]
        # Pick diverse findings across images (max 5)
        flaw_findings = self._pick_diverse_findings(flaw_findings, 5)
        generic_shots = [s for s in storyboard if s.get("shot") is not None]
        flaw_shots = self._identify_flaw_shots(generic_shots, flaw_findings)

        # Ensure we have enough flaw_shots for the findings
        while len(flaw_shots) < len(flaw_findings):
            flaw_shots.append({})

        # ── Episode-specific config ──
        theme_labels = {
            "text-garbling": {
                "keyword": "文字乱码",
                "color": "#ff1744",
                "checks": [
                    {"label": "文字清晰度", "fail": "✗ 乱码", "pass": "✓ 清晰"},
                    {"label": "字符形状", "fail": "✗ 畸形", "pass": "✓ 方正"},
                    {"label": "笔画完整", "fail": "✗ 断裂", "pass": "✓ 完整"},
                ],
                "summary": "记住查三处：文字清晰度 · 字符形状 · 笔画完整",
                "teaser": "下期：光影破绽——AI不懂物理定律 →",
            },
            "hand-flaw": {
                "keyword": "手指异常",
                "color": "#ff1744",
                "checks": [
                    {"label": "手指数量", "fail": "✗ 异常", "pass": "✓ 正常"},
                    {"label": "关节弯曲", "fail": "✗ 僵直", "pass": "✓ 自然"},
                    {"label": "手指比例", "fail": "✗ 失调", "pass": "✓ 正常"},
                ],
                "summary": "记住查三处：手指数量 · 关节弯曲 · 手指比例",
                "teaser": "下期：文字乱码——AI不识字 →",
            },
            "face-flaw": {
                "keyword": "面部异常",
                "color": "#ff9100",
                "checks": [
                    {"label": "五官对称", "fail": "✗ 歪斜", "pass": "✓ 对称"},
                    {"label": "瞳孔形状", "fail": "✗ 异常", "pass": "✓ 正常"},
                    {"label": "皮肤纹理", "fail": "✗ 塑料感", "pass": "✓ 自然"},
                ],
                "summary": "记住查三处：五官对称 · 瞳孔形状 · 皮肤纹理",
                "teaser": "下期：手指破绽——AI永远画不好手 →",
            },
            "generic": {
                "keyword": "AI破绽",
                "color": "#ff1744",
                "checks": [
                    {"label": "手指数量", "fail": "✗ 异常", "pass": "✓ 正常"},
                    {"label": "五官对称", "fail": "✗ 歪斜", "pass": "✓ 对称"},
                    {"label": "文字清晰度", "fail": "✗ 乱码", "pass": "✓ 清晰"},
                ],
                "summary": "记住查三处：手 · 脸 · 文字",
                "teaser": "下期见 →",
            },
        }
        tc = theme_labels.get(theme, theme_labels["generic"])

        # Build timing: allocate from timing array, use defaults for auto-inserted
        ti = 0
        def _next_t(default_dur=5.0):
            nonlocal ti
            if ti < len(timing):
                t = timing[ti]
                ti += 1
                return t["start"], t["duration"]
            return 0.0, default_dur

        # ── Hook → social-frame ──
        hook_shot = generic_shots[0] if generic_shots else {}
        hook_start, hook_dur = _next_t(3.0)
        scenes.append({
            "component": "social-frame",
            "start": hook_start,
            "duration": hook_dur,
            "config": {
                "username": "小美",
                "avatar_letter": "美",
                "post_text": hook_shot.get("caption", hook_shot.get("audio", "聚会太开心啦！")),
                "post_time": "2小时前",
                "img_src": primary_img,
                "likes": "156",
                "comments": [
                    ("小芳", "在哪里拍的？好好看！"),
                    ("阿杰", "这是AI生成的吧？"),
                    ("小美 回复 阿杰", "怎么可能~"),
                ],
            },
        })

        # ── Glitch transition (auto-inserted, fixed 2s) ──
        glitch_start = hook_start + hook_dur - 0.5
        scenes.append({
            "component": "glitch-transition",
            "start": glitch_start,
            "duration": 2.0,
            "config": {},
        })
        reveal_start = glitch_start + 1.5

        # ── Reveal text ──
        reveal_texts = {
            "text-garbling": "背景里的招牌泄露了天机。<br/>AI不识字——全是乱码。",
            "hand-flaw": "它不是真人拍的。<br/>是AI生成的。",
            "face-flaw": "它不是真人拍的。<br/>是AI生成的。",
            "generic": "它不是真人拍的。<br/>是AI生成的。",
        }
        scenes.append({
            "component": "reveal-text",
            "start": reveal_start,
            "duration": 3.0,
            "config": {
                "reveal_text": reveal_texts.get(theme, reveal_texts["generic"]),
                "anticipation_text": "来，我放大三个细节给你看 ↓",
                "img_src": primary_img,
            },
        })

        # ── Flaw zoom shots → zoom-analyze ──
        zoom_start = reveal_start + 2.5
        label_prefixes = "①②③④⑤"
        colors = {"hand": "#ff1744", "face": "#ff9100", "text": "#ff1744", "texture": "#e040fb"}

        for i, (fshot, finding) in enumerate(zip(flaw_shots, flaw_findings)):
            if ti < len(timing):
                shot_t = timing[ti]
                ti += 1
                dur = shot_t["duration"]
            else:
                dur = 5.0

            img_num = i + 2
            cx = finding.get("cx", 540)
            cy = finding.get("cy", 960)
            score = finding.get("score", 0.5)
            desc = finding.get("desc", tc["keyword"])
            detector = finding.get("detector", "")
            # Use the finding's source image if available, else primary
            src_img = finding.get("_image", primary_img) or primary_img
            # For text detector, always use "文字乱码" as keyword
            if detector == "text":
                kt = "文字乱码"
            else:
                kt = desc

            kw_color = colors.get(detector, tc["color"])
            zoom = 3.0 if detector == "face" else 2.6

            config = {
                "label": f"{label_prefixes[i]} 看{desc}",
                "label_id": f"lbl{img_num}",
                "img_id": f"img{img_num}",
                "img_src": src_img,
                "zoom_origin_x": cx,
                "zoom_origin_y": cy,
                "zoom_scale": zoom,
                "keyword_text": kt,
                "keyword_color": kw_color,
                "keyword_id": f"kw{img_num}",
                "keyword_top": 760,
                "keyword_left": 100,
                "keyword_delay": 1.5,
                "markers": [
                    {"id": f"mk{img_num}a", "x": cx, "y": cy,
                     "w": 140, "h": 140, "delay": 1.5},
                    {"id": f"mk{img_num}b", "x": cx + 80, "y": cy - 40,
                     "w": 100, "h": 100, "delay": 2.3},
                ],
                "data_badge": {
                    "top": 680, "right": 70,
                    "big": f"{score:.0%}" if score <= 1 else f"{score:.1f}",
                    "sub": "异常指数",
                },
                "data_id": f"dv{img_num}",
                "data_delay": 3.0,
                "count_badge": {"top": 1020, "right": 80, "value": str(i + 1)},
                "count_id": f"cb{img_num}",
                "count_delay": 3.8,
                "zoom_out_at": zoom_start + dur - 1.0,
            }
            scenes.append({
                "component": "zoom-analyze",
                "start": zoom_start,
                "duration": dur,
                "config": config,
            })
            zoom_start += dur

        # ── Compare split (or summary if no real photo) ──
        comp_start = zoom_start + 0.5
        checks = tc["checks"]
        summary = tc["summary"]
        # Collect meaningful flaw descriptions
        seen_descs = set()
        unique_descs = []
        for f in flaw_findings[:3]:
            d = f.get("desc", "")
            if d and d not in seen_descs:
                unique_descs.append(d)
                seen_descs.add(d)
        if len(unique_descs) >= 3:
            checks = [
                {"label": unique_descs[0], "fail": "✗ 异常", "pass": "✓ 正常"},
                {"label": unique_descs[1], "fail": "✗ 歪斜", "pass": "✓ 对称"},
                {"label": unique_descs[2], "fail": "✗ 僵直", "pass": "✓ 自然"},
            ]
            summary = "记住查三处：" + " · ".join(unique_descs[:3])

        if real_img and real_img != primary_img:
            # Have a distinct comparison image → full compare-split
            scenes.append({
                "component": "compare-split",
                "start": comp_start,
                "duration": 10.0,
                "config": {
                    "ai_img": primary_img,
                    "real_img": real_img,
                    "checks": checks,
                    "summary_text": summary,
                },
            })

        # ── Outro ──
        scenes.append({
            "component": "outro",
            "start": comp_start + 10.0,
            "duration": 10.0,
            "config": {
                "title": _brand_name(),
                "subtitle": "关注我，下次被骗的不是你",
                "teaser": tc["teaser"],
                "logo_char": "鉴",
            },
        })

        return scenes

    # ─── Helpers ─────────────────────────────────────────────

    def _load_profile(self, video_type: str) -> list[ShotMapping]:
        if video_type in ("ai-flaw-detect", "ai_flaw_detect"):
            return AI_FLAW_DETECT_PROFILE
        return AI_FLAW_DETECT_PROFILE

    def _extract_findings(self, report: dict) -> list[dict]:
        """Extract flaw findings from analysis report, sorted by score.

        Tag each finding with its source image so the mapper can use the
        right image per zoom-analyze component.
        """
        results = report.get("results", [report])
        if isinstance(results, dict):
            results = [results]
        all_items = []
        for r in results:
            img = r.get("image", "")
            for d in r.get("detector_results", []):
                for f in d.get("findings", []):
                    f["detector"] = d.get("detector", "unknown")
                    f["_image"] = img
                    all_items.append(f)
        # Sort: text findings first (most visible/episode-relevant), then by score
        def _sort_key(f):
            is_text = 0 if f.get("detector") == "text" else 1
            return (is_text, -f.get("score", 0))
        all_items.sort(key=_sort_key)
        return all_items

    def _pick_diverse_findings(self, findings: list[dict], count: int = 5) -> list[dict]:
        """Pick top findings while ensuring diversity across source images."""
        picked = []
        seen_images = set()
        # First pass: pick one finding per image
        for f in findings:
            img = f.get("_image", "")
            if img not in seen_images and len(picked) < count:
                picked.append(f)
                seen_images.add(img)
        # Second pass: fill remaining slots with highest-scored unused findings
        for f in findings:
            if f not in picked and len(picked) < count:
                picked.append(f)
        return picked

    def _detect_episode_theme(self, findings: list[dict]) -> str:
        """Detect episode theme from finding types (text/hand/face/texture)."""
        if not findings:
            return "generic"
        counts = {}
        for f in findings:
            d = f.get("detector", "unknown")
            counts[d] = counts.get(d, 0) + 1
        total = sum(counts.values())
        if counts.get("text", 0) / total > 0.3:
            return "text-garbling"
        if counts.get("hand", 0) / total > 0.3:
            return "hand-flaw"
        if counts.get("face", 0) / total > 0.3:
            return "face-flaw"
        return "generic"

    def _extract_images(self, report: dict) -> list[str]:
        """Extract image paths from analysis report."""
        results = report.get("results", [report])
        if isinstance(results, dict):
            results = [results]
        return [r.get("image", "") for r in results if r.get("image")]

    def _pick_real_image(self, report: dict, primary_img: str) -> str:
        """Pick the best comparison image.

        Priority:
        1. User-provided real photo in output dir (real_photo.png / real_photo.jpg)
        2. Image with fewest AI flaws (fallback, but may still be AI-generated)
        3. Primary image (last resort)
        """
        # Check for user-provided real photo in common locations
        import glob as _glob
        candidates = []
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        for pattern in ["**/real_photo.*", "**/real_comparison.*"]:
            candidates.extend(_glob.glob(os.path.join(output_dir, pattern), recursive=True))

        for cand in candidates:
            if os.path.isfile(cand) and os.path.getsize(cand) > 10000:
                return os.path.basename(cand)  # relative to assets dir

        # Fallback: image with fewest findings
        results = report.get("results", [report])
        if isinstance(results, dict):
            results = [results]
        best_img = ""
        best_count = 10**9
        for r in results:
            img = r.get("image", "")
            count = r.get("total_findings", 0)
            # Heavily penalize text-garbled findings — real photos shouldn't have them
            text_count = 0
            for d in r.get("detector_results", []):
                if d.get("detector") == "text":
                    text_count = d.get("count", 0)
            adjusted = count + text_count * 5  # text garbling is strong AI signal
            if adjusted < best_count and img != primary_img:
                best_count = adjusted
                best_img = img
        return best_img or primary_img

    def _identify_flaw_shots(self, shots: list[dict],
                             findings: list[dict]) -> list[dict]:
        """Identify storyboard shots that map to zoom-analyze components."""
        flaw_shots = []
        for shot in shots:
            visual = shot.get("visual", "")
            if "放大" in visual or "标注" in visual or "圆圈" in visual:
                flaw_shots.append(shot)
        if not flaw_shots and len(shots) >= 4:
            mid_shots = [s for s in shots
                         if "对比" not in s.get("visual", "")
                         and "总结" not in s.get("visual", "")
                         and "关注" not in s.get("visual", "")
                         and "Logo" not in s.get("visual", "")]
            flaw_shots = mid_shots[1:min(4, len(mid_shots))]
        return flaw_shots

    def _progress_segments(self, scenes: list[dict],
                           total_dur: float) -> list[dict]:
        """Generate progress bar segment markers from scene boundaries."""
        segments = []
        for s in scenes:
            if s["component"] in ("reveal-text", "zoom-analyze",
                                   "compare-split", "outro"):
                segments.append({"start": s["start"]})
        return segments

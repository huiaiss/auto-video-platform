"""JianyingDraftExporter — component storyboard → Jianying (剪映) .draft folder.

Generates a fully editable Jianying project from the CompositionBuilder's
component storyboard. Users open the draft in Jianying for final tweaks.

Route A features:
  - Scale keyframes for zoom-analyze (100% → 300% zoom animation)
  - Scene-to-scene transitions (dissolve/slide/blur per beat type)
  - Audio fade-out on narration track
  - SRT subtitle import via TextSegment (since pyJianYingDraft lacks native caption API)

Key mappings:
    social-frame → image + styled text overlays
    glitch-transition → RGB split effect
    reveal-text → text with bounce-in animation
    zoom-analyze → image + keyframe scale + marker text + keyword tag
    compare-split → two images side-by-side + checklist text
    outro → logo + title + CTA text
    scan-overlay → holographic scan effect
    progress-bar → (skipped — Jianying has its own playback progress)

Usage:
    from builders.jianying_exporter import JianyingDraftExporter
    exporter = JianyingDraftExporter()
    draft_path = exporter.export(component_storyboard_dict)
    # → %LOCALAPPDATA%/JianyingPro/User Data/Projects/com.local/
"""

import os, sys, uuid, shutil
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Lazy import — only when actually exporting
# ---------------------------------------------------------------------------

_JY_AVAILABLE = False
try:
    import pyJianYingDraft as _draft
    from pyJianYingDraft import (
        trange,
        TextIntro, TextOutro, TextLoopAnim,
        VideoSceneEffectType, FontType, TextStyle, ClipSettings,
        IntroType, OutroType, TrackType, TransitionType,
        VideoSegment, TextSegment, AudioSegment, ScriptFile, DraftFolder,
        KeyframeProperty,
    )
    _JY_AVAILABLE = True
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Jianying draft path discovery
# ---------------------------------------------------------------------------

def find_jianying_draft_dir() -> Optional[str]:
    """Locate Jianying's draft directory on this machine."""
    localappdata = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        os.path.join(localappdata, "JianyingPro", "User Data", "Projects", "com.local"),
        os.path.join(localappdata, "JianyingPro Drafts"),
        os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "JianyingPro", "User Data", "Projects", "com.local"),
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return None


# ---------------------------------------------------------------------------
# Style presets matching our component visuals
# ---------------------------------------------------------------------------

# Colors in Jianying's 0-1 RGB space
CYBER_GREEN = (0.0, 0.9, 0.46)      # #00e676
NEON_RED = (1.0, 0.09, 0.27)        # #ff1744
NEON_AMBER = (1.0, 0.57, 0.0)       # #ff9100
WHITE = (1.0, 1.0, 1.0)
DARK_BG = (0.02, 0.02, 0.04)        # #06060b
GRAY = (0.5, 0.5, 0.5)
GOLD = (0.93, 0.75, 0.42)           # #ecbe6b

TITLE_STYLE = TextStyle(
    size=8.0,
    color=WHITE,
    bold=True,
    align=1,  # center
)

SUBTITLE_STYLE = TextStyle(
    size=5.0,
    color=CYBER_GREEN,
    bold=True,
    align=1,
)

BODY_STYLE = TextStyle(
    size=4.0,
    color=(0.87, 0.87, 0.87),
    align=0,  # left
)

KEYWORD_STYLE = TextStyle(
    size=6.0,
    color=NEON_RED,
    bold=True,
    align=1,
)

LABEL_STYLE = TextStyle(
    size=3.5,
    color=CYBER_GREEN,
    bold=False,
    align=0,
)

CHECKLIST_FAIL_STYLE = TextStyle(
    size=4.5,
    color=NEON_RED,
    bold=True,
    align=2,  # right
)

CHECKLIST_PASS_STYLE = TextStyle(
    size=4.5,
    color=CYBER_GREEN,
    bold=True,
    align=2,
)


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------

class JianyingDraftExporter:
    """Export a component storyboard as a Jianying editable draft project."""

    def __init__(self, draft_dir: str = None):
        if not _JY_AVAILABLE:
            raise ImportError(
                "pyJianYingDraft is required. Install: pip install pyJianYingDraft"
            )
        self.draft_dir = draft_dir or find_jianying_draft_dir()
        self._draft: Optional[ScriptFile] = None
        self._material_idx = 0
        self._text_tracks = []
        self._text_track_idx = 0
        self._video_tracks = []
        self._video_track_idx = 0
        # Route A: track last video segment per track for scene transitions
        self._last_video_seg = None
        self._last_component = ""
        self._subtitle_track_idx = 0

    # ─── Public API ──────────────────────────────────────────

    def export(self, storyboard: dict, draft_name: str = None,
               assets_dir: str = None, srt_path: str = "") -> str:
        """Convert component storyboard → Jianying .draft folder.

        Args:
            storyboard: dict with 'scenes' list (same format as CompositionBuilder input)
            draft_name: name for the Jianying project
            assets_dir: directory containing source images (for copying into draft)
            srt_path: optional path to SRT subtitle file for native subtitle track

        Returns:
            Path to the created draft folder
        """
        draft_name = draft_name or f"AI_{uuid.uuid4().hex[:6]}"

        # Determine output directory
        if assets_dir:
            output_root = os.path.abspath(assets_dir)
        else:
            output_root = os.path.join(os.path.dirname(__file__), "..", "output", "jianying")
        os.makedirs(output_root, exist_ok=True)

        # Create draft via pyJianYingDraft
        if self.draft_dir:
            folder = DraftFolder(self.draft_dir)
            self._draft = folder.create_draft(
                draft_name, width=1080, height=1920, fps=24
            )
        else:
            # Standalone: write draft to our output directory
            draft_folder = os.path.join(output_root, draft_name)
            os.makedirs(draft_folder, exist_ok=True)
            self._draft = ScriptFile(
                width=1080, height=1920, fps=24, maintrack_adsorb=True
            )
            self._draft.save_path = os.path.join(draft_folder, "draft_content.json")

        # Reset per-export state
        self._text_tracks = []
        self._text_track_idx = 0
        self._video_tracks = []
        self._video_track_idx = 0
        self._last_video_seg = None
        self._last_component = ""
        self._subtitle_track_idx = 0

        # Set up tracks (multiple video + text tracks to avoid overlaps)
        self._draft.add_track(TrackType.audio)
        self._video_tracks = []
        self._video_track_idx = 0
        self._text_tracks = []
        self._text_track_idx = 0
        # Main video track for sequential scenes (enables transitions)
        self._draft.add_track(TrackType.video, track_name="video_main")
        # Additional video tracks for overlapping segments
        for i in range(19):
            self._draft.add_track(TrackType.video, track_name=f"video_{i}")
            self._video_tracks.append(f"video_{i}")
        for i in range(20):
            track_name = f"text_{i}"
            self._draft.add_track(TrackType.text, track_name=track_name)
            self._text_tracks.append(track_name)

        # Dedicated subtitle tracks — round-robin to avoid segment overlap
        self._subtitle_tracks = []
        for i in range(10):
            track_name = f"subtitles_{i}"
            self._draft.add_track(TrackType.text, track_name=track_name)
            self._subtitle_tracks.append(track_name)
        self._subtitle_track_idx = 0

        scenes = storyboard.get("scenes", [])
        audio_src = storyboard.get("audio_src", "")

        # Copy assets into draft materials folder
        materials_dir = self._prepare_materials(scenes, assets_dir)

        # Add audio track with fade-out
        if audio_src and os.path.exists(audio_src):
            self._add_audio(audio_src, storyboard)

        # Import SRT subtitles if available
        srt = srt_path or storyboard.get("srt_path", "")
        if srt and os.path.exists(srt):
            self._add_subtitles_from_srt(srt)

        # Process each scene → Jianying segments
        for i, scene in enumerate(scenes):
            comp = scene.get("component", "")
            cfg = scene.get("config", {})
            start_s = scene.get("start", 0.0)
            dur_s = scene.get("duration", 5.0)

            method = getattr(self, f"_export_{comp.replace('-', '_')}", None)
            if method:
                method(cfg, start_s, dur_s, materials_dir)
                self._last_component = comp
            else:
                print(f"  [JY] Skipped unknown component: {comp}")

        # Save the draft
        self._draft.save()
        draft_path = self._draft.save_path or os.path.dirname(
            getattr(self._draft, 'save_path', ''))
        print(f"[JianyingExporter] Draft saved: {draft_path}")
        return draft_path

    # ─── Component exporters ─────────────────────────────────

    def _export_social_frame(self, cfg: dict, start: float, dur: float,
                             mats: str):
        """Social frame → image + styled social-media UI text blocks."""
        img_src = cfg.get("img_src", "")
        img_path = self._resolve_asset(img_src, mats)
        username = cfg.get("username", "用户")
        post_text = cfg.get("post_text", "")
        likes = cfg.get("likes", "128")
        comments = cfg.get("comments", [])
        avatar = cfg.get("avatar_letter", username[0])

        # Background image
        if img_path and os.path.exists(img_path):
            seg = VideoSegment(img_path, trange(f"{start}s", f"{dur}s"))
            seg.add_animation(IntroType.from_name("渐显"))
            self._add_video(seg)

        # Username + avatar badge
        self._add_text(
            f"◉ {username}",
            start + 0.6, 1.5,
            style=TextStyle(size=4.5, color=GOLD, bold=True),
            y_pos=-0.65, intro_name="弹簧",
        )

        # Post text (caption)
        if post_text:
            self._add_text(
                post_text[:60],
                start + 0.9, 2.5,
                style=TextStyle(size=4.0, color=WHITE),
                y_pos=-0.45, intro_name="渐显",
            )

        # Likes
        self._add_text(
            f"❤ {likes}人赞了",
            start + 1.8, 0.8,
            style=TextStyle(size=3.5, color=GRAY),
            y_pos=-0.18, intro_name="渐显",
        )

        # Comments (up to 3)
        for i, (name, text) in enumerate(comments[:3]):
            self._add_text(
                f"{name}：{text}",
                start + 2.3 + i * 0.4, 1.0,
                style=TextStyle(size=3.0, color=(0.8, 0.8, 0.8)),
                y_pos=-0.05 + i * 0.1, intro_name="向左滑动",
            )

    def _export_glitch_transition(self, cfg: dict, start: float, dur: float,
                                  mats: str):
        """Glitch → RGB split effect + glitch video effect."""
        # Add RGB split effect as a standalone effect track (idempotent)
        if "glitch_fx" not in self._draft.tracks:
            self._draft.add_track(TrackType.effect, "glitch_fx")
        try:
            self._draft.add_effect(
                VideoSceneEffectType.from_name("故障"),
                trange(f"{start}s", f"{dur-0.3}s"),
                track_name="glitch_fx",
                params=[None, None, 80.0],
            )
        except Exception:
            # Fallback: try edge glitch
            try:
                self._draft.add_effect(
                    VideoSceneEffectType.from_name("边缘glitch"),
                    trange(f"{start}s", f"{dur-0.3}s"),
                    track_name="glitch_fx",
                    params=[None, None, 70.0],
                )
            except Exception:
                pass

    def _export_reveal_text(self, cfg: dict, start: float, dur: float,
                            mats: str):
        """Reveal → dark BG + photo fade + big red reveal text."""
        img_src = cfg.get("img_src", "")
        img_path = self._resolve_asset(img_src, mats)
        reveal = cfg.get("reveal_text", "它不是真人拍的。").replace("<br/>", " ")
        anticipation = cfg.get("anticipation_text", "来，我放大给你看 ↓")

        # Image at reduced opacity (dark bg is implicit)
        if img_path and os.path.exists(img_path):
            seg = VideoSegment(img_path, trange(f"{start}s", f"{dur}s"))
            seg.add_animation(IntroType.from_name("渐显"))
            self._add_video(seg)

        # Big red reveal text — bounce in
        self._add_text(
            reveal, start + 0.5, 1.8,
            style=TextStyle(size=9.0, color=NEON_RED, bold=True),
            y_pos=-0.15, intro_name="弹簧", loop_name="放大缩小",
        )

        # Anticipation subtitle
        self._add_text(
            anticipation, start + 2.2, 1.5,
            style=TextStyle(size=5.5, color=WHITE, bold=True),
            y_pos=0.1, intro_name="向上滑动",
        )

    def _export_zoom_analyze(self, cfg: dict, start: float, dur: float,
                             mats: str):
        """Zoom-analyze → image + keyframe scale + marker text + keyword tag + data badge.

        Route A: adds scale_x/scale_y keyframes for animated zoom effect:
          0.0s → 1.0x  (normal)
          1.0s → zoom_scale (zoom in)
          dur-1.0s → zoom_scale (hold)
          dur-0.3s → 1.0x (zoom out for next scene)
        """
        img_src = cfg.get("img_src", "")
        img_path = self._resolve_asset(img_src, mats)
        label = cfg.get("label", "")
        keyword = cfg.get("keyword_text", "")
        kw_color_raw = cfg.get("keyword_color", "#ff1744")
        markers = cfg.get("markers", [])
        data_badge = cfg.get("data_badge", {})
        count_badge = cfg.get("count_badge", {})
        zoom_scale = float(cfg.get("zoom_scale", 2.6))

        # Parse keyword color
        kw_color = self._parse_color(kw_color_raw, NEON_RED)

        # Image on timeline with animated scale keyframes
        if img_path and os.path.exists(img_path):
            seg = VideoSegment(img_path, trange(f"{start}s", f"{dur}s"))
            seg.add_animation(IntroType.from_name("渐显"))

            # Route A: scale keyframes — zoom in → hold → zoom out
            zoom_in_at = int(1.0 * 1_000_000)
            hold_at = int(max(1.5, dur - 1.0) * 1_000_000)
            zoom_out_at = int(max(2.0, dur - 0.3) * 1_000_000)

            seg.add_keyframe(KeyframeProperty.scale_x, 0, 1.0)
            seg.add_keyframe(KeyframeProperty.scale_y, 0, 1.0)
            seg.add_keyframe(KeyframeProperty.scale_x, zoom_in_at, zoom_scale)
            seg.add_keyframe(KeyframeProperty.scale_y, zoom_in_at, zoom_scale)
            seg.add_keyframe(KeyframeProperty.scale_x, hold_at, zoom_scale)
            seg.add_keyframe(KeyframeProperty.scale_y, hold_at, zoom_scale)
            seg.add_keyframe(KeyframeProperty.scale_x, zoom_out_at, 1.0)
            seg.add_keyframe(KeyframeProperty.scale_y, zoom_out_at, 1.0)

            self._add_video(seg)

        # Scene label (top-left, green)
        if label:
            self._add_text(
                label, start + 0.6, dur - 0.5,
                style=TextStyle(size=3.5, color=CYBER_GREEN, bold=False),
                y_pos=-0.88, x_pos=-0.85,
                intro_name="向左滑动",
            )

        # Keyword tag (big, colored, center)
        if keyword:
            self._add_text(
                keyword, start + 1.5, 2.5,
                style=TextStyle(size=7.0, color=kw_color, bold=True),
                y_pos=-0.25, intro_name="弹簧", loop_name="放大缩小",
            )

        # Marker labels (small circles aren't possible, use text marks instead)
        for i, mk in enumerate(markers):
            delay = mk.get("delay", 1.5 + i * 0.8)
            mk_x = mk.get("x", 540) / 1080.0 * 2 - 1  # normalize to -1..1
            mk_y = mk.get("y", 960) / 1920.0 * 2 - 1
            self._add_text(
                "◉", start + delay, 2.0,
                style=TextStyle(size=5.0, color=NEON_RED, bold=True),
                y_pos=mk_y * 0.7, x_pos=mk_x * 0.7,
                intro_name="随机弹跳",
            )

        # Data badge
        if data_badge:
            big = data_badge.get("big", "")
            sub = data_badge.get("sub", "")
            db_text = f"{big} {sub}" if sub else big
            if db_text:
                self._add_text(
                    db_text, start + 3.0, 2.0,
                    style=TextStyle(size=5.0, color=NEON_RED, bold=True),
                    y_pos=-0.5, x_pos=0.65,
                    intro_name="向右滑动",
                )

        # Count badge
        if count_badge:
            val = count_badge.get("value", "")
            if val:
                self._add_text(
                    f"破绽 {val}", start + 4.0, 1.5,
                    style=TextStyle(size=5.5, color=NEON_RED, bold=True),
                    y_pos=0.6, x_pos=0.7,
                    intro_name="随机弹跳",
                )

    def _export_compare_split(self, cfg: dict, start: float, dur: float,
                              mats: str):
        """Compare split → AI vs Real side-by-side + checklist."""
        ai_img = cfg.get("ai_img", "")
        real_img = cfg.get("real_img", "")
        ai_path = self._resolve_asset(ai_img, mats)
        real_path = self._resolve_asset(real_img, mats)
        checks = cfg.get("checks", [])
        summary = cfg.get("summary_text", "")

        # Left: AI image (scaled to left half)
        if ai_path and os.path.exists(ai_path):
            seg = VideoSegment(ai_path, trange(f"{start+0.3}s", f"{dur-0.6}s"))
            seg.add_animation(IntroType.from_name("向左滑动"))
            # Position: left half via clip_settings
            seg.clip_settings = ClipSettings(
                transform_x=-0.25,  # left half
                scale_x=0.48,
                scale_y=0.48,
            )
            self._add_video(seg)

        # Right: Real image
        if real_path and os.path.exists(real_path):
            seg = VideoSegment(real_path, trange(f"{start+0.3}s", f"{dur-0.6}s"))
            seg.add_animation(IntroType.from_name("向右滑动"))
            seg.clip_settings = ClipSettings(
                transform_x=0.25,   # right half
                scale_x=0.48,
                scale_y=0.48,
            )
            self._add_video(seg)

        # AI badge (top of left panel)
        self._add_text(
            "✗ AI生成", start + 0.6, dur - 0.5,
            style=TextStyle(size=3.8, color=NEON_RED, bold=True),
            y_pos=-0.62, x_pos=-0.35, intro_name="渐显",
        )

        # Real badge (top of right panel)
        self._add_text(
            "✓ 真人照片", start + 0.6, dur - 0.5,
            style=TextStyle(size=3.8, color=CYBER_GREEN, bold=True),
            y_pos=-0.62, x_pos=0.42, intro_name="渐显",
        )

        # VS divider
        self._add_text(
            "VS", start + 0.7, 1.5,
            style=TextStyle(size=7.0, color=WHITE, bold=True),
            y_pos=-0.35, intro_name="随机弹跳",
        )

        # Checklist rows
        for i, ch in enumerate(checks):
            label = ch.get("label", "")
            fail = ch.get("fail", "")
            row_text = f"{label}  {fail}"
            self._add_text(
                row_text, start + 1.9 + i * 0.7, 1.8,
                style=TextStyle(size=4.2, color=NEON_RED, bold=False),
                y_pos=0.4 + i * 0.12, intro_name="向左滑动",
            )

        # Summary text
        if summary:
            self._add_text(
                summary, start + 1.3, dur - 1.0,
                style=TextStyle(size=6.5, color=WHITE, bold=True),
                y_pos=0.7, intro_name="向上滑动",
            )

    def _export_outro(self, cfg: dict, start: float, dur: float, mats: str):
        """Outro → logo ring + title + CTA subtitle + teaser."""
        title = cfg.get("title", "AI照妖镜")
        subtitle = cfg.get("subtitle", "关注我，下次被骗的不是你")
        teaser = cfg.get("teaser", "下期见 →")
        logo_char = cfg.get("logo_char", "鉴")

        # Logo char (big centered)
        self._add_text(
            logo_char, start + 0.4, dur - 0.5,
            style=TextStyle(size=20.0, color=CYBER_GREEN, bold=True),
            y_pos=-0.3, intro_name="随机弹跳", loop_name="放大缩小",
        )

        # Title
        self._add_text(
            title, start + 1.2, dur - 1.0,
            style=TextStyle(size=9.0, color=WHITE, bold=True),
            y_pos=0.05, intro_name="向上滑动",
        )

        # CTA subtitle
        self._add_text(
            subtitle, start + 1.8, dur - 1.5,
            style=TextStyle(size=5.0, color=CYBER_GREEN, bold=True),
            y_pos=0.18, intro_name="渐显",
        )

        # Teaser
        if teaser:
            self._add_text(
                teaser, start + 2.7, dur - 2.0,
                style=TextStyle(size=4.0, color=GRAY),
                y_pos=0.3, intro_name="向左滑动",
            )

    def _export_scan_overlay(self, cfg: dict, start: float, dur: float,
                             mats: str):
        """Scan overlay → holographic scan effect on a dedicated track."""
        show_at = cfg.get("show_at", start)
        hide_at = cfg.get("hide_at", start + dur)

        if "scan_fx" not in self._draft.tracks:
            self._draft.add_track(TrackType.effect, "scan_fx")
        try:
            self._draft.add_effect(
                VideoSceneEffectType.from_name("全息扫描"),
                trange(f"{show_at}s", f"{hide_at}s"),
                track_name="scan_fx",
                params=[None, None, 60.0],
            )
        except Exception:
            # Fallback: use any available scan-like effect
            pass

    def _export_progress_bar(self, cfg: dict, start: float, dur: float,
                             mats: str):
        """Progress bar — skipped. Jianying has its own playback progress."""
        pass  # Jianying's built-in playback bar serves this purpose

    # ─── Helpers ─────────────────────────────────────────────

    def _add_video(self, seg, mats: str = ""):
        """Add a video segment with track selection and scene transition logic.

        Route A: adjacent non-overlapping video segments go on the same track
        so that scene-to-scene transitions work (pyJianYingDraft transitions
        only apply between adjacent segments on a single track).
        Overlapping segments use round-robin tracks to avoid collisions.
        """
        # Use round-robin tracks for overlapping scenes, main track for sequential
        if self._last_video_seg is not None:
            last_end = self._last_video_seg.target_timerange.end
            curr_start = seg.target_timerange.start
            can_share_track = curr_start >= last_end - 50000  # 50ms tolerance
        else:
            can_share_track = True

        if can_share_track:
            track_name = "video_main"
            # Route A: add transition between consecutive scenes on same track
            if self._last_video_seg is not None and self._last_component != "glitch-transition":
                ttype = self._pick_transition(self._last_component)
                if ttype:
                    try:
                        seg.add_transition(ttype, duration="0.5s")
                    except Exception:
                        pass
        else:
            track_name = self._video_tracks[self._video_track_idx % len(self._video_tracks)]
            self._video_track_idx += 1

        self._draft.add_segment(seg, track_name=track_name)
        self._last_video_seg = seg

    def _pick_transition(self, from_component: str):
        """Pick an appropriate transition type based on the preceding component."""
        mapping = {
            "social-frame": "叠化",
            "reveal-text": "模糊放大",
            "zoom-analyze": "模糊",
            "compare-split": "叠化",
            "outro": None,
        }
        name = mapping.get(from_component, "叠化")
        if name is None:
            return None
        try:
            return TransitionType.from_name(name)
        except Exception:
            return None

    def _add_text(self, text: str, start: float, duration: float,
                  style: TextStyle = None, y_pos: float = 0.0,
                  x_pos: float = 0.0,
                  intro_name: str = None, outro_name: str = None,
                  loop_name: str = None):
        """Add a text segment with optional animations.

        Uses round-robin across multiple text tracks to avoid overlap errors.
        """
        seg = TextSegment(
            text,
            trange(f"{start}s", f"{duration}s"),
            style=style or BODY_STYLE,
            clip_settings=ClipSettings(
                transform_y=y_pos,
                transform_x=x_pos,
            ),
        )

        # Animations (loop must be added AFTER intro/outro)
        if intro_name:
            try:
                seg.add_animation(TextIntro.from_name(intro_name))
            except Exception:
                pass
        if outro_name:
            try:
                seg.add_animation(TextOutro.from_name(outro_name))
            except Exception:
                pass
        if loop_name:
            try:
                seg.add_animation(TextLoopAnim.from_name(loop_name))
            except Exception:
                pass

        # Round-robin across text tracks to avoid segment overlap
        track_name = self._text_tracks[self._text_track_idx % len(self._text_tracks)]
        self._text_track_idx += 1
        self._draft.add_segment(seg, track_name=track_name)

    def _add_audio(self, audio_path: str, storyboard: dict = None):
        """Add narration audio track with fade-out in last 2 seconds."""
        if os.path.exists(audio_path):
            dur = self._get_audio_duration(audio_path)
            seg = AudioSegment(audio_path, trange("0s", f"{dur}s"))
            # Route A: audio fade-out — volume 1.0 → 0.0 over last 2s
            fade_start = max(0, dur - 2.0)
            seg.add_keyframe(int(fade_start * 1_000_000), 1.0)
            seg.add_keyframe(int((dur - 0.1) * 1_000_000), 0.0)
            self._draft.add_segment(seg)

    def _add_subtitles_from_srt(self, srt_path: str):
        """Parse SRT file and create TextSegment subtitles via round-robin tracks.

        Since pyJianYingDraft lacks a native caption API, we use TextSegment
        positioned at the bottom of the screen with standard subtitle styling.
        Multiple tracks prevent segment overlap errors.
        """
        entries = self._parse_srt(srt_path)
        if not entries:
            return

        sub_style = TextStyle(
            size=5.0,
            color=WHITE,
            bold=True,
            align=1,
        )

        for start_sec, end_sec, text in entries:
            dur = max(0.1, end_sec - start_sec)
            seg = TextSegment(
                text,
                trange(f"{start_sec}s", f"{dur}s"),
                style=sub_style,
                clip_settings=ClipSettings(
                    transform_y=0.78,
                    transform_x=0.0,
                ),
            )
            try:
                seg.add_animation(TextIntro.from_name("渐显"))
            except Exception:
                pass
            track_name = self._subtitle_tracks[self._subtitle_track_idx % len(self._subtitle_tracks)]
            self._subtitle_track_idx += 1
            self._draft.add_segment(seg, track_name=track_name)

        print(f"  [JY] Imported {len(entries)} subtitle entries from SRT")

    @staticmethod
    def _parse_srt(srt_path: str) -> list[tuple[float, float, str]]:
        """Parse an SRT file into (start, end, text) tuples."""
        entries = []
        try:
            with open(srt_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return entries

        import re
        blocks = re.split(r"\n\s*\n", content.strip())
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 3:
                continue
            # Parse timing line: "00:00:01,000 --> 00:00:04,000"
            time_match = re.match(
                r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})",
                lines[1],
            )
            if not time_match:
                continue
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, time_match.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
            text = " ".join(lines[2:]).replace("\n", " ").strip()
            if text:
                entries.append((start, end, text))
        return entries

    def _resolve_asset(self, src: str, materials_dir: str) -> str:
        """Resolve an asset path — copy to materials dir if needed."""
        if not src:
            return ""
        if os.path.isabs(src) and os.path.exists(src):
            return src
        # Try relative to materials dir
        candidate = os.path.join(materials_dir, os.path.basename(src))
        if os.path.exists(candidate):
            return candidate
        # Try as-is
        if os.path.exists(src):
            return src
        return ""

    def _prepare_materials(self, scenes: list, assets_dir: str = None) -> str:
        """Copy all referenced assets into the draft's materials folder."""
        if hasattr(self._draft, '_materials_dir') and self._draft._materials_dir:
            materials = self._draft._materials_dir
        elif self._draft.save_path:
            materials = os.path.join(os.path.dirname(self._draft.save_path), "materials")
        else:
            materials = os.path.join(os.path.dirname(__file__), "..", "output", "jianying", "materials")
        os.makedirs(materials, exist_ok=True)

        if assets_dir and os.path.isdir(assets_dir):
            for f in os.listdir(assets_dir):
                src = os.path.join(assets_dir, f)
                dst = os.path.join(materials, f)
                if os.path.isfile(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)

        # Also copy any referenced images from scenes
        for scene in scenes:
            for key in ("img_src", "ai_img", "real_img"):
                src = scene.get("config", {}).get(key, "")
                if src and os.path.isfile(src):
                    dst = os.path.join(materials, os.path.basename(src))
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)

        return materials

    @staticmethod
    def _get_audio_duration(path: str) -> float:
        """Get audio duration in seconds."""
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True,
            )
            return float(result.stdout.strip())
        except Exception:
            return 30.0

    @staticmethod
    def _parse_color(hex_str: str, default: tuple) -> tuple:
        """Parse '#ff1744' → (1.0, 0.09, 0.27)."""
        try:
            h = hex_str.lstrip("#")
            return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        except Exception:
            return default

"""BGM Mixer — multi-track background music pre-mixing via ffmpeg.

Supports multiple BGM tracks with independent start times, durations, and volumes.
Pre-mixes everything into a single audio file so the browser only handles one <audio> tag.

Usage:
    from builders.bgm_mixer import BGMMixer
    mixer = BGMMixer(bgm_dir="bgm_library")
    output = mixer.mix([
        {"src": "cyber_intro.mp3", "start": 0, "end": 8, "volume": 0.3},
        {"src": "tense_beat.mp3", "start": 8, "end": 30, "volume": 0.2},
    ], total_duration_s=37, output_path="output/bgm_mixed.mp3")

BGM Library:
    bgm_library/
    ├── cyber_intro.mp3     赛博朋克开场 — 短促有力，适合前3秒钩子
    ├── tense_beat.mp3       悬疑律动 — 持续低音，适合分析/放大环节
    ├── tech_explain.mp3     科技讲解 — 轻电子，适合原理/数据卡片
    ├── reveal_punch.mp3     揭示重音 — 节奏重拍，适合破绽标注瞬间
    └── outro_rise.mp3       结尾上扬 — 渐强收尾，适合CTA/关注引导
"""

import os, subprocess, shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── BGM Track Definition ───────────────────────────────────

@dataclass
class BGMTrack:
    """A single BGM segment with timeline placement."""
    src: str              # File path or BGM library name
    start: float = 0.0    # Timeline start (seconds)
    end: float = 0.0      # Timeline end (seconds)
    volume: float = 0.25  # 0.0–1.0

    @property
    def duration(self) -> float:
        return max(0, self.end - self.start)


# ─── Curated BGM Presets ─────────────────────────────────────

# Emotion → BGM mapping: each beat gets its own track based on emotion.
# Like a real editor: hook gets a stinger, reveal gets a hit, analysis gets a loop.
EMOTION_BGM_MAP: dict[str, str] = {
    "hook":      "stinger_hit",     # 开场钩子 — 短促冲击
    "surprise":  "reveal_hit",      # 破绽揭示 — 重音强调
    "curiosity": "tense_loop",      # 悬念/分析 — 持续低音
    "trust":     "ambient_pad",     # 原理讲解 — 轻电子底
    "desire":    "tense_loop",      # 引导 — 同悬念
    "action":    "energy_beat",     # CTA / 收藏转发 — 节奏上扬
    "default":   "ambient_pad",     # 兜底
}

# Legacy — kept for backward compatibility
AI_FLAW_DETECT_PRESET: list[dict] = [
    {"name": "cyber_intro",   "start": 0,  "end_rel": "hook_end", "volume": 0.30},
    {"name": "tense_beat",    "start": "hook_end", "end_rel": "checklist_start", "volume": 0.22},
    {"name": "outro_rise",    "start": "checklist_start", "end_rel": "end", "volume": 0.30},
]


# ─── Mixer ───────────────────────────────────────────────────

class BGMMixer:
    """Pre-mixes multiple BGM tracks into a single audio file using ffmpeg."""

    def __init__(self, bgm_dir: str = None):
        self.bgm_dir = Path(bgm_dir) if bgm_dir else Path(__file__).parent.parent / "bgm_library"

    def mix(self, tracks: list[dict], total_duration_s: float,
            output_path: str = None) -> str:
        """Mix multiple BGM tracks into one audio file.

        Args:
            tracks: list of {"src", "start", "end", "volume"} dicts
            total_duration_s: total video duration (truncates output)
            output_path: destination .mp3 path

        Returns:
            Path to mixed MP3 file
        """
        if not tracks:
            return ""

        output = Path(output_path) if output_path else Path("bgm_mixed.mp3")
        output.parent.mkdir(parents=True, exist_ok=True)

        # Resolve source files (check bgm_dir first, then as absolute path)
        resolved_tracks = []
        for t in tracks:
            src = self._resolve_src(t["src"])
            if not src:
                print(f"  [BGM] WARNING: source not found: {t['src']}")
                continue
            resolved_tracks.append({
                "src": src,
                "start": float(t.get("start", 0)),
                "end": float(t.get("end", total_duration_s)),
                "volume": float(t.get("volume", 0.25)),
            })

        if not resolved_tracks:
            print("  [BGM] No valid tracks to mix")
            return ""

        # Single track — just trim + adjust volume, no mixing needed
        if len(resolved_tracks) == 1:
            return self._process_single(resolved_tracks[0], total_duration_s, str(output))

        # Multi-track — use ffmpeg filter_complex
        return self._process_multi(resolved_tracks, total_duration_s, str(output))

    def _resolve_src(self, src: str) -> Optional[str]:
        """Resolve BGM source: check bgm_dir first, then as-is."""
        # Check in bgm_library
        candidate = self.bgm_dir / src
        if candidate.exists():
            return str(candidate)
        # Check with .mp3 extension
        if not src.endswith(".mp3"):
            candidate = self.bgm_dir / f"{src}.mp3"
            if candidate.exists():
                return str(candidate)
        # Check as absolute/relative path
        if os.path.exists(src):
            return src
        return None

    def _process_single(self, track: dict, total_dur: float, output: str) -> str:
        """Process a single BGM track: trim + volume."""
        dur = min(track["end"] - track["start"], total_dur - track["start"])
        if dur <= 0:
            return ""

        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-i", track["src"],
            "-af", f"atrim={track['start']}:{track['start']+dur},"
                   f"volume={track['volume']},"
                   f"afade=t=out:st={dur-1.5}:d=1.5",
            "-t", str(total_dur),
            output,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return output
        except subprocess.CalledProcessError as e:
            print(f"  [BGM] Single-track mix failed: {e.stderr.decode()[:200] if e.stderr else e}")
            return ""

    def _process_multi(self, tracks: list[dict], total_dur: float, output: str) -> str:
        """Mix multiple BGM tracks with ffmpeg filter_complex."""
        # Build filter graph
        inputs = []
        filter_parts = []
        labels = []

        for i, t in enumerate(tracks):
            dur = min(t["end"] - t["start"], total_dur - t["start"])
            if dur <= 0:
                continue

            inputs.extend(["-i", t["src"]])
            label = f"a{i}"
            labels.append(label)

            delay_ms = int(t["start"] * 1000)
            fade_out_start = max(0, dur - 1.5)

            filter_parts.append(
                f"[{i}:a]atrim=0:{dur},"
                f"adelay={delay_ms}|{delay_ms},"
                f"volume={t['volume']},"
                f"afade=t=out:st={fade_out_start}:d=1.5"
                f"[{label}]"
            )

        if not labels:
            return ""

        mix_inputs = "".join(f"[{l}]" for l in labels)
        filter_parts.append(
            f"{mix_inputs}amix=inputs={len(labels)}:duration=first:dropout_transition=0[out]"
        )

        filter_graph = ";".join(filter_parts)

        cmd = [
            "ffmpeg", "-y", "-v", "error",
            *inputs,
            "-filter_complex", filter_graph,
            "-map", "[out]",
            "-t", str(total_dur),
            output,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            print(f"  [BGM] Mixed {len(labels)} tracks → {output}")
            return output
        except subprocess.CalledProcessError as e:
            print(f"  [BGM] Multi-track mix failed: {e.stderr.decode()[:200] if e.stderr else e}")
            return ""

    def build_preset(self, preset: list[dict], beat_times: dict,
                     total_duration_s: float) -> list[dict]:
        """Expand a preset template with actual beat timing values.

        Args:
            preset: template list with "end_rel" keys referencing beat names
            beat_times: {"hook_end": 3.0, "checklist_start": 21.0, "end": 37.0}
            total_duration_s: total video time

        Returns:
            List of resolved {"src", "start", "end", "volume"} dicts
        """
        resolved = []
        for t in preset:
            start = t["start"]
            if isinstance(start, str):
                start = beat_times.get(start, 0)
            end = t["end_rel"]
            if isinstance(end, str):
                end = beat_times.get(end, total_duration_s)

            resolved.append({
                "src": t["name"],
                "start": float(start),
                "end": float(end),
                "volume": float(t.get("volume", 0.25)),
            })
        return resolved

    @staticmethod
    def build_beat_tracks(script, total_duration_s: float) -> list[dict]:
        """Build per-beat BGM tracks — like a real editor placing clips on a timeline.

        Each beat gets its own BGM clip based on its emotion.
        Adjacent beats with the same BGM are merged into one continuous segment.
        Cross-fade gaps (0.3s) are inserted between different BGM segments.

        Returns:
            List of {"src", "start", "end", "volume"} dicts, one per beat group.
        """
        # Calculate beat start times
        beat_starts = {}
        t = 0.0
        for b in script.beats:
            beat_starts[b.index] = t
            t += b.duration_s
        outro_start = t
        outro_end = outro_start + script.outro.duration_s

        # Assign BGM to each beat by emotion
        beat_bgm = []
        for b in script.beats:
            bgm_name = EMOTION_BGM_MAP.get(b.emotion, EMOTION_BGM_MAP["default"])
            beat_bgm.append({
                "beat_idx": b.index,
                "bgm": bgm_name,
                "start": beat_starts[b.index],
                "end": beat_starts[b.index] + b.duration_s,
                "emotion": b.emotion,
            })

        # Outro always gets energy_beat or outro_rise
        outro_bgm = "energy_beat" if script.outro.emotion in ("action",) else "ambient_pad"
        beat_bgm.append({
            "beat_idx": "outro",
            "bgm": outro_bgm,
            "start": outro_start,
            "end": outro_end,
            "emotion": script.outro.emotion,
        })

        # Merge adjacent beats that use the same BGM
        merged = []
        for bgm in beat_bgm:
            if merged and merged[-1]["bgm"] == bgm["bgm"]:
                # Extend the previous segment
                merged[-1]["end"] = bgm["end"]
            else:
                merged.append(dict(bgm))

        # Convert to track dicts with volume
        # Hook gets louder, analysis gets quieter, action gets medium
        vol_map = {"hook": 0.30, "surprise": 0.28, "curiosity": 0.20,
                   "trust": 0.18, "action": 0.25, "default": 0.20}

        tracks = []
        for m in merged:
            vol = vol_map.get(m["emotion"], 0.20)
            tracks.append({
                "src": m["bgm"],
                "start": m["start"],
                "end": m["end"],
                "volume": vol,
            })

        return tracks


# ─── BGM Library Bootstrap ───────────────────────────────────

def bootstrap_bgm_library(bgm_dir: str = None) -> Path:
    """Create bgm_library/ directory with README and download instructions.

    The actual .mp3 files need to be sourced by the user (copyright).
    This creates a structured directory with recommendations.
    """
    import json

    root = Path(bgm_dir) if bgm_dir else Path(__file__).parent.parent / "bgm_library"
    root.mkdir(parents=True, exist_ok=True)

    readme = root / "README.md"
    readme.write_text("""# BGM Library — AI照妖镜

## 目录结构
每段视频按节奏分3段BGM:

```
bgm_library/
├── cyber_intro.mp3      # 赛博朋克开场 — 短促有力，前3秒钩子
├── tense_beat.mp3        # 悬疑律动 — 持续低音，分析/放大环节
├── tech_explain.mp3      # 科技讲解 — 轻电子，原理/数据卡片
├── reveal_punch.mp3      # 揭示重音 — 节奏重拍，破绽标注
└── outro_rise.mp3        # 结尾上扬 — 渐强收尾，CTA引导
```

## 如何获取BGM

### 方法1: 抖音热门BGM提取
1. 打开抖音, 搜索"科技科普"类视频
2. 点击右下角"音乐"图标查看BGM名称
3. 在网易云音乐/QQ音乐搜索同名BGM
4. 下载后放入本目录, 按上方命名规则重命名

### 方法2: 免费商用BGM网站
- **Pixabay Music** (https://pixabay.com/music/) — 搜索 cyberpunk/electronic/tense
- **YouTube Audio Library** — 搜索 "tech" "suspense" "electronic"
- **Freesound** (https://freesound.org/) — 搜索 "cyberpunk" "glitch" "beat"

### 方法3: AI生成BGM
- **Suno AI** (https://suno.ai) — 输入 "赛博朋克风格电子音乐, 30秒, 适合科技科普视频"
- **AIVA** (https://aiva.ai) — AI作曲, 可选风格模板

## BGM推荐(抖音科技类同款风格)
| 风格 | 参考BGM名 | 适用场景 |
|------|-----------|----------|
| 赛博朋克 | Cyberpunk 2077 OST 风格 | 开场钩子 |
| 悬疑电子 | Stranger Things 风格合成器 | 分析破绽 |
| 轻科技 | Blade Runner 风格环境音 | 原理讲解 |
| 重拍提示 | 鼓点+贝斯 | 破绽标注 |
""", encoding="utf-8")

    print(f"  [BGM] Library bootstrapped at: {root}")
    print(f"  [BGM] Next: download 3-5 .mp3 files into {root}/")
    return root

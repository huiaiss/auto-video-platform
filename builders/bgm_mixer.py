#!/usr/bin/env python
"""BGM Mixer — Ducking 混音引擎

使用 ffmpeg sidechaincompress 实现口播时 BGM 自动降低 (ducking)。
当口播开始时，BGM 音量在 3ms 内降低 6-8dB；口播结束后 50ms 平滑恢复。

Usage:
    mixer = BGMMixer()
    result = mixer.mix(
        video_path="output/stage3/_texted.mp4",
        narration_path="output/stage3/narration.mp3",
        bgm_path="assets/bgm/corporate_tech.mp3",
        output_path="output/stage3/_with_bgm.mp4",
        total_duration_s=34.0,
    )
"""

import os, subprocess, json, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BGMMixer:
    """Sidechain Compression 混音器 — 口播时 BGM 自动 ducking。"""

    # 默认 EQ 曲线：削减 BGM 低频/中低频，让人声更清晰
    DEFAULT_EQ = (
        "equalizer=f=120:t=q:w=1:g=-4,"  # 减 120Hz 隆隆声
        "equalizer=f=400:t=q:w=1:g=-3,"  # 减 400Hz 浑浊
        "equalizer=f=2000:t=q:w=1:g=-2," # 微减 2kHz
        "equalizer=f=8000:t=q:w=0.5:g=-1" # 微减 8kHz
    )

    def __init__(self, threshold=0.25, ratio=4, attack=3, release=60, makeup=1):
        """
        Args:
            threshold: sidechain 触发阈值 (0.0-1.0)，口播超过此值则触发 ducking
            ratio: 压缩比 (4:1 ≈ 降低 6-8dB)
            attack: 压缩启动时间 (ms)，越小响应越快
            release: 压缩释放时间 (ms)，越大恢复越平滑
            makeup: 补偿增益 (dB)，压缩后整体音量提升
        """
        self.threshold = threshold
        self.ratio = ratio
        self.attack = attack
        self.release = release
        self.makeup = makeup

    def mix(self, video_path, narration_path, bgm_path, output_path,
            total_duration_s=None, bgm_volume=0.15, voice_volume=1.0,
            bgm_eq=True):
        """执行 ducking 混音。

        Args:
            video_path: 带画面的视频文件（无需音频，或音频将被替换）
            narration_path: 口播音频文件 (WAV/MP3)
            bgm_path: BGM 音频文件
            output_path: 输出 MP4 路径
            total_duration_s: 视频总时长 (s)，用于 fade out
            bgm_volume: BGM 基础音量 (0-1)
            voice_volume: 口播音量 (0-1)
            bgm_eq: 是否应用 BGM EQ 削减

        Returns:
            dict: {success: bool, output_path: str, error: str|None}
        """
        # 参数校验
        for p in [video_path, narration_path, bgm_path]:
            if not os.path.exists(p):
                return {"success": False, "output_path": None,
                        "error": f"File not found: {p}"}

        # 获取视频时长作为 fade out 参考
        if total_duration_s is None:
            total_duration_s = self._ffprobe_duration(video_path)

        # ==== 构建 FFmpeg filter graph ====
        # 输入：
        #   0:v — 视频流
        #   1:a — BGM
        #   2:a — 口播 (narration)
        #
        # 信号链：
        #   [2:a] volume + loudnorm → voice
        #   [1:a] volume + EQ + fade → bgm
        #   [bgm][voice] sidechaincompress → bgm_ducked
        #   [bgm_ducked][voice] amix → [a] 最终音频

        # === 构建 FFmpeg filter graph ===
        # 输入索引：
        #   0:v — 视频 (输入文件1: _texted.mp4, 可能无音频)
        #   1:a — BGM (输入文件2: bgm.mp3)
        #   2:a — 口播 (输入文件3: narration.mp3)
        #
        # 关键：口播 [voice] 需要 asplit=2 分成两路，
        #       一路给 sidechaincompress 做控制信号，
        #       另一路给最终 amix

        # Pad narration to match video duration (avoid truncation)
        pad_dur = total_duration_s + 2  # +2s safety margin
        voice_chain = "[2:a]volume=1.0"
        voice_chain += ",aresample=48000:async=1:first_pts=0"  # 统一采样率，复位 PTS
        voice_chain += f",apad=whole_dur={pad_dur}"  # 补齐到视频长度
        voice_chain += "[voice]"

        bgm_chain = f"[1:a]volume={bgm_volume}"
        if bgm_eq:
            bgm_chain += f",aresample=48000,{self.DEFAULT_EQ}"
        else:
            bgm_chain += ",aresample=48000"
        fade_start = max(total_duration_s - 2, 0)
        bgm_chain += f",afade=t=out:st={fade_start}:d=2[bgm]"

        # asplit: voice → [voice_sc] (for sidechain) + [voice_mix] (for final mix)
        split_chain = "[voice]asplit=2[voice_sc][voice_mix]"

        # sidechaincompress: BGM 被口播压缩
        sc_params = (
            f"threshold={self.threshold}:"
            f"ratio={self.ratio}:"
            f"attack={self.attack}:"
            f"release={self.release}:"
            f"makeup={self.makeup}"
        )
        sc_chain = f"[bgm][voice_sc]sidechaincompress={sc_params}[bgm_ducked]"

        # 最终混合：压缩后的 BGM + 原始口播
        mix_chain = "[bgm_ducked][voice_mix]amix=inputs=2:duration=first:dropout_transition=2[a]"

        filter_complex = ";".join([
            voice_chain, bgm_chain, split_chain, sc_chain, mix_chain
        ])

        # ==== 执行 FFmpeg ====
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", bgm_path,
            "-i", narration_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-filter_complex", filter_complex,
            "-map", "[a]",
            "-t", str(total_duration_s),
            output_path,
        ]

        try:
            r = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=600
            )
            if r.returncode != 0:
                err = r.stderr[-500:] if r.stderr else "Unknown error"
                return {"success": False, "output_path": None, "error": err}

            if not os.path.exists(output_path):
                return {"success": False, "output_path": None,
                        "error": "Output not created"}

            return {
                "success": True,
                "output_path": output_path,
                "size_mb": os.path.getsize(output_path) / 1024 / 1024,
                "error": None,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "output_path": None,
                    "error": "FFmpeg timeout (600s)"}
        except Exception as e:
            return {"success": False, "output_path": None,
                    "error": str(e)}

    def mix_preview(self, narration_path, bgm_path, output_path,
                    total_duration_s=10, bgm_volume=0.15):
        """快速生成 10 秒混音 demo（只有音频，用于验证 ducking 效果）。

        Args:
            narration_path: 口播音频
            bgm_path: BGM 文件
            output_path: 输出音频路径 (.mp3/.m4a)
            total_duration_s: 混音时长 (s)
            bgm_volume: BGM 基础音量
        """
        filters = [
            f"[1:a]volume={bgm_volume},aresample=48000,afade=t=out:st={total_duration_s-1}:d=1[bgm]",
            f"[2:a]volume=1.0,aresample=48000:async=1:first_pts=0[voice]",
            "[voice]asplit=2[voice_sc][voice_mix]",
            f"[bgm][voice_sc]sidechaincompress="
            f"threshold={self.threshold}:ratio={self.ratio}:"
            f"attack={self.attack}:release={self.release}:makeup={self.makeup}[bgm_d]",
            "[bgm_d][voice_mix]amix=inputs=2:duration=first:dropout_transition=2[a]",
        ]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
            "-i", bgm_path,
            "-i", narration_path,
            "-filter_complex", ";".join(filters),
            "-map", "[a]",
            "-t", str(total_duration_s),
            "-c:a", "aac", "-b:a", "128k",
            output_path,
        ]

        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        return r.returncode == 0

    @staticmethod
    def _ffprobe_duration(path):
        """用 ffprobe 获取文件时长 (s)。"""
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", path],
            capture_output=True, text=True, timeout=30
        )
        try:
            return float(r.stdout.strip())
        except (ValueError, TypeError):
            return 30.0


# ===== 快速验证 =====
if __name__ == "__main__":
    import sys, tempfile

    # 找最新一次 pipeline 产出的文件
    s3 = os.path.join(ROOT, "output", "stage3")
    narration = os.path.join(s3, "narration.mp3")
    bgm = os.path.join(ROOT, "assets", "bgm", "corporate_tech.mp3")

    if not os.path.exists(narration) or not os.path.exists(bgm):
        print("Need: narration.mp3 and corporate_tech.mp3")
        sys.exit(1)

    # 生成 10 秒 ducking demo（纯音频）
    demo_path = os.path.join(s3, "_ducking_demo.mp3")
    mixer = BGMMixer(threshold=0.25, ratio=4, attack=3, release=60)

    print("=" * 60)
    print("Ducking 混音验证 — 10s demo")
    print("=" * 60)
    print(f"  阈值: {mixer.threshold}")
    print(f"  压缩比: {mixer.ratio}:1")
    print(f"  Attack: {mixer.attack}ms | Release: {mixer.release}ms")
    print(f"  BGM: {bgm}")
    print(f"  口播: {narration}")
    print()

    ok = mixer.mix_preview(narration, bgm, demo_path, total_duration_s=10)
    if ok:
        print(f"  ✅ Demo: {demo_path}")
        print(f"     大小: {os.path.getsize(demo_path)//1024}KB")
        print()
        print("  👂 请用耳机听 _ducking_demo.mp3 验证：")
        print("     口播开始时 BGM 应自动降低 6-8dB")
        print("     口播结束后 BGM 应平滑恢复")
        print()
    else:
        print("  ❌ Demo FAILED")

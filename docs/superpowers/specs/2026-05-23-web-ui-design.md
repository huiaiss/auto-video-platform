# Auto Video Platform — Web UI Design Spec

**Date:** 2026-05-23
**Status:** Approved
**Framework:** Gradio

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│ Top Bar: Provider Status (LLM: ONLINE | TTS: ONLINE) │
├────────┬────────────┬──────────┬────────────────────┤
│ 快速生成 │  批量队列   │ 历史记录  │      设置          │
├────────┴────────────┴──────────┴────────────────────┤
│                                                      │
│  ┌──── Left 280px ────┐  ┌──── Right (flex) ───────┐│
│  │                     │  │                          ││
│  │ Video Type ▼        │  │  7-Stage Progress        ││
│  │ Topic/Title         │  │  Script Preview          ││
│  │ Upload Image (drop)  │  │  Audio Waveform          ││
│  │ TTS Voice ▼         │  │  Video Player            ││
│  │                     │  │                          ││
│  │ [▶ 一键生成视频]    │  │                          ││
│  │                     │  │                          ││
│  └─────────────────────┘  └──────────────────────────┘│
└──────────────────────────────────────────────────────┘
```

**Four tabs:**
- **快速生成** — main workspace, left config + right preview
- **批量队列** — submit multiple tasks, sequential execution
- **历史记录** — past videos with play/download/re-generate
- **设置** — LLM/TTS config, brand DNA, defaults

---

## 2. Quick Generate Tab (Core)

### 2.1 Config Panel (Left, 280px fixed)

| Field | Component | Default | Notes |
|-------|-----------|---------|-------|
| 视频类型 | Dropdown | "AI鉴定" | 5 options: AI鉴定 / 带货种草 / 工厂宣传 / 知识教程 / 个人Vlog |
| 选题/主题 | Textbox | "" | Auto-populated if reference image uploaded |
| 参考图片 | File Upload (drag) | None | Shows thumbnail after upload |
| TTS配音 | Dropdown | "云希Neural" | Populated from available TTS providers |
| 语速 | Slider | 1.1 | Range 0.5-2.0 |
| 生成模式 | Radio | "一键到底" | "一键到底" / "逐步确认" |
| BGM | Checkbox | Off | |
| 导出剪映草稿 | Checkbox | Off | Generates 剪映 draft after Stage 7 |
| 品牌 | Textbox | "AI照妖镜" | |

**Bottom:** Big red button "一键生成视频" (estimated time shown below)

### 2.2 Progress / Preview Area (Right, flex)

Two rendering modes:

**Mode A: 一键到底** — All 7 stages auto-execute, live progress shown as vertical list:
- Each stage = collapsible card with status icon (○ pending / ● running / ✓ done / ✗ failed)
- Stage 2 (Script) auto-expands to show beat list
- Stage 7 (Render) shows final video player on completion
- Stage 8 (剪映) auto-exports draft file if checkbox enabled

**Mode B: 逐步确认** — Pauses at 3 key checkpoints:
- Stage 2 pause: user can edit beat text/animation/duration, re-run quality check, then click "继续"
- Stage 4 pause: user can preview audio, switch TTS provider, then click "继续"
- Stage 5 pause: user can review matched assets, replace individual images, then click "继续"
- Stages 1, 3, 6, 7, 8 run without pausing (no user input needed)

### 2.3 8-Stage Pipeline Display

```
✓ Stage 1: 参考图分析 (1.2s)
✓ Stage 2: AI脚本生成 (15.3s) — 9 Beats, 51s, 100分
  Beat1 [hook  ] 3.0s "这台绕线机的精度，太离谱了..."
  Beat2 [trust ] 5.0s "线槽均匀度，肉眼可见的差距"
  ...
● Stage 3: 质量检查 (0.5s)
○ Stage 4: TTS配音
○ Stage 5: 素材匹配
○ Stage 6: HTML组装
○ Stage 7: MP4渲染
○ Stage 8: 导出剪映草稿 (仅当勾选时执行)
```

Each completed stage shows elapsed time. Failed stages show error message with retry button.

### 2.4 剪映导出 (Stage 8)

**入口:** 配置栏底部 checkbox "导出剪映草稿"（默认关闭）

**行为:**
- Stage 7 MP4 渲染完成后，自动生成剪映草稿文件
- 草稿包含：音频轨、SRT字幕轨、图片素材轨（按 Beat 排列）、动画关键帧
- 导出完成后右侧显示 "剪映草稿已生成：[打开目录]" 链接
- 用户双击草稿文件即可在剪映中打开，手动精调（加贴纸、转场、文字特效等）

**技术实现:** 复用现有 `builders/jianying_exporter.py`，输出为剪映可导入的 JSON draft 格式。

---

## 3. Batch Queue Tab

### Layout
```
┌─ Add Task Bar ──────────────────────────────────────┐
│ Topic: [__________] Type: [▼] Image: [📎] [+ Add]   │
└───────────────────────────────────────────────────────┘
┌─ Queue (3 items) ──────── [▶ Start All] [🗑 Clear] ─┐
│ #1 无刷电机绕线机  工厂宣传  ● Stage 4/7  ████░░ 57% │
│ #2 AI文字破绽      AI鉴定    ○ Waiting               │
│ #3 绕线精度对比    工厂宣传  ○ Waiting               │
└───────────────────────────────────────────────────────┘
```

### Behavior
- Tasks execute sequentially (Chromium can only render one at a time)
- Failed tasks auto-skip, remaining queue continues
- Completed tasks show play/download buttons inline
- Add-bar stays visible during execution (can add while queue runs)

---

## 4. History Tab

### Layout
Each history item = horizontal card:
```
┌──┬──────────────────────────────────────┐
│  │ 视频标题                   05-23 20:17│
│封│ 工厂宣传 | 51s | 100分               │
│面│ ▶ 播放  ⬇ 下载MP4  📄 脚本  🔄 重新生成│
└──┴──────────────────────────────────────┘
```

### Features
- **Search** by title keyword
- **Filter** by video type dropdown
- **Sort** by date (newest first)
- **Pagination** (8 per page)
- Each card has 4 actions: play video inline, download MP4, view script JSON, re-generate with same params
- Re-generate opens a pre-filled Quick Generate tab

### Data Storage
History stored as `output/<project>/metadata.json` per project.
Tab scans all `output/*/metadata.json` files to build the list.

---

## 5. Settings Tab

### 5.1 LLM Provider Config
- Chip-style provider selector: DeepSeek / Qwen / Ollama / Moonshot
- Online/offline status indicator per provider
- Priority order shown (arrows between chips)
- API key input (masked, stored in `.env` via python-dotenv)
- Test connection button per provider

### 5.2 TTS Provider Config
- Voice dropdown (populated from current provider's voice list)
- Speed slider (0.5 - 2.0)
- Preview button: synthesizes a short sample and plays it
- Provider status indicator

### 5.3 Brand DNA
| Field | Type | Example |
|-------|------|---------|
| 品牌名 | Textbox | "AI照妖镜" |
| 标语 | Textbox | "关注AI照妖镜，下次被骗的不是你" |
| 视觉风格 | Textbox | "深色背景+霓虹绿标注+红色高亮" |
| 语气 | Textbox | "冷静客观+略带犀利+口语化" |
| BGM风格 | Dropdown | "赛博朋克电子" / "科技大气" / "轻快电子" / etc. |
| 结尾模板 | Textbox | "关注{brand_name}，{slogan}" |

### 5.4 Defaults
- 默认视频类型 dropdown
- 默认TTS配音 dropdown
- 输出根目录 textbox (default: `output/`)
- 自动打开预览 checkbox (default: on)

---

## 6. Technical Implementation

### 6.1 Stack
- **UI Framework:** Gradio 4.x (Blocks API for multi-tab layout)
- **Backend:** Direct Python calls to existing `pipeline.py` modules
- **State:** `gr.State()` for session state, JSON files for persistence
- **Async:** Gradio's built-in queue system for pipeline execution

### 6.2 File Structure (New Files)
```
d:/auto-video-platform/
├── app.py                    # Gradio entry point (new)
├── app/
│   ├── __init__.py           # (new)
│   ├── tabs/
│   │   ├── __init__.py       # (new)
│   │   ├── generate_tab.py   # Quick Generate tab (new)
│   │   ├── batch_tab.py      # Batch Queue tab (new)
│   │   ├── history_tab.py    # History tab (new)
│   │   └── settings_tab.py   # Settings tab (new)
│   └── components/
│       ├── __init__.py       # (new)
│       ├── progress.py       # 7-stage progress component (new)
│       └── pipeline_runner.py # Async pipeline executor (new)
├── config/
│   ├── llm_config.json       # (existing)
│   ├── tts_config.json       # (existing)
│   └── brand_dna.json        # Brand DNA presets (new)
└── pipeline.py               # (existing, already wired)
```

### 6.3 Key Architectural Decisions

1. **No subprocess** — Gradio calls pipeline functions directly (same process). No API server needed.
2. **Generator-based progress** — pipeline yields progress events via Python generator, Gradio renders them in real-time via `gr.Progress()`
3. **History via filesystem scan** — no database. Scans `output/*/metadata.json`. Simple and portable.
4. **Settings persistence** — writes to `.env` (API keys) + `config/*.json` (preferences). `python-dotenv` handles reload.
5. **Single Chromium lock** — only one MP4 render at a time. Batch queue enforces this.

### 6.4 Pipeline Integration

```python
# app/components/pipeline_runner.py
def run_pipeline_yielding(video_type, topic, ref_image, voice, speed, ...):
    """Generator that yields (stage, status, data) tuples for real-time UI updates."""
    pipeline = VideoPipeline()
    
    yield (1, "running", {})
    ref_analysis = pipeline._analyze_ref(ref_image)
    yield (1, "done", ref_analysis)
    
    yield (2, "running", {})
    script = pipeline._generate_script(...)
    yield (2, "done", {"script": script})
    
    # ... stages 3-7
    yield (7, "done", {"mp4_path": mp4_path})
```

Gradio's `every=` or queue system consumes this generator and updates the UI.

---

## 7. What We're NOT Building (Yet)

- User authentication / login
- Cloud deployment (local first, `share=True` for simple sharing)
- Mobile responsive (desktop-only, 1080p target)
- Database (filesystem is sufficient for single-user/small-team)
- Scheduled posting to Douyin
- Real-time collaborative editing

---

## 8. Launch Command

```bash
cd d:/auto-video-platform
python app.py
# Opens browser at http://127.0.0.1:7860
# For team sharing: python app.py --share  (generates public URL)
```

---

## 9. Verification Checklist

- [ ] Quick Generate: upload image → select type → click generate → MP4 appears
- [ ] Quick Generate (逐步模式): pauses at script, can edit and continue
- [ ] Batch Queue: add 3 tasks → start all → all 3 complete sequentially
- [ ] History: shows past videos, can play/download/re-generate
- [ ] Settings: change TTS voice → new voice used in next generation
- [ ] Settings: change brand DNA → new brand info in next script
- [ ] Provider status: shows online/offline in top bar
- [ ] Error handling: bad image → graceful error message, not crash

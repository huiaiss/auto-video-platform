# Codex Context Checkpoint
> Auto-saved: 2026-06-05 01:34

## Current Pipeline State
- Pipeline: **S1+S2+S3**
- Script: 电机定子绕线内幕 (7 beats, content_share)
- final.mp4: 5988KB

## Config
- TTS voice: longxiaochun
- Script mode: content (default) / add -m for marketing

## Key Decisions
- HDR->SDR: reinhard tonemap
- BGM: mixkit_107.mp3 (227s)
- TTS: Ark TTS via proxy :8791
- Audio: loudnorm I=-16 after SFX mix
- Script: content_share (default) / viral_short (-m)
- Emotion audit: hook + trust|proof + action|save
- xfade 0.3s, CRF 18, preset slow

## Architecture
- pipeline.py — main pipeline
- go.py — one-click runner
- config/tts_config.json — TTS providers
- generators/ark_tts_proxy.py — TTS proxy :8791
- generators/tts_providers.py — TTS dispatcher
- auditors/audit_*.py — 3 audits
- configs/brands/taizhou_longjiang.json — brand

## Footage
- D:/隆江视频素材/IMG_0346~0349.MP4 (4 files, HDR HLG)
- Output: output/stage3/final.mp4

## Session Rules
1. Read _CONTEXT.md + shared-context.md at session start
2. go.py = full pipeline; python pipeline.py [0-3] = single stage
3. Audit must PASS before next stage
4. Default mode = content_share (no marketing CTA)

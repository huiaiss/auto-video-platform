import os, json, subprocess, datetime
ROOT = r"D:\auto-video-platform"
CTX = os.path.join(ROOT, "_CONTEXT.md")
def collect_state():
    state = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "last_final_mp4": "", "stage3_size": "", "script_info": "", "current_tts_voice": "", "script_mode": "", "pipeline_state": ""}
    s3 = os.path.join(ROOT, "output", "stage3", "final.mp4")
    if os.path.exists(s3):
        sz = os.path.getsize(s3) // 1024
        state["last_final_mp4"] = s3
        state["stage3_size"] = f"{sz}KB"
    s2 = os.path.join(ROOT, "output", "stage2", "script.json")
    if os.path.exists(s2):
        try:
            sc = json.load(open(s2, encoding="utf-8"))
            state["script_info"] = f'{sc.get("title","?")} ({len(sc.get("beats",[]))} beats, {sc.get("metadata",{}).get("video_type","?")})'
        except: pass
    s1ok = os.path.join(ROOT, "output", "stage1", "AUDIT_PASS.txt")
    s2ok = os.path.join(ROOT, "output", "stage2", "AUDIT_PASS.txt")
    s3ok = os.path.join(ROOT, "output", "stage3", "AUDIT_PASS.txt")
    parts = []
    if os.path.exists(s1ok): parts.append("S1")
    if os.path.exists(s2ok): parts.append("S2")
    if os.path.exists(s3ok): parts.append("S3")
    state["pipeline_state"] = "+".join(parts) if parts else "empty"
    tts_cfg = os.path.join(ROOT, "config", "tts_config.json")
    if os.path.exists(tts_cfg):
        try:
            cfg = json.load(open(tts_cfg, encoding="utf-8"))
            state["current_tts_voice"] = cfg.get("default_voice", "?")
        except: pass
    return state
def write_context(state):
    content = f"""# Codex Context Checkpoint
> Auto-saved: {state["timestamp"]}

## Current Pipeline State
- Pipeline: **{state["pipeline_state"]}**
- Script: {state["script_info"]}
- final.mp4: {state["stage3_size"]}

## Config
- TTS voice: {state["current_tts_voice"]}
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
"""
    with open(CTX, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Context saved. State: {state['pipeline_state']} | {state['script_info']}")
if __name__ == "__main__":
    write_context(collect_state())
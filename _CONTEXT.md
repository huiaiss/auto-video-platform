# Auto Video Platform — 项目状态 v4
> 2026-06-12 | 架构：Hermes → Claude | Codex 已裁撤

## 团队架构 (v4)
```
老板(用户) = 终审
  └── Hermes = 调度 + 审计（不执行）
        └── Claude = 创意 + 执行（avp + cxp 全包）
              Codex = 已裁撤
```

## 通信
飞书 → feishu-bridge → task-board.json ← Hermes Loop(5min)
Hermes → subprocess → Claude CLI

## 模型路由
- smart_proxy :15721 → DeepSeek
- 豆包 doubao → vision 专用

## 管线状态 (Stage 1-3 全 PASS)
- Stage 1 粗剪 ✅ | Stage 2 脚本 ✅ | Stage 3 合成 ✅
- final.mp4: output/stage3/final.mp4 (31.9MB)
- completed.marker: VERIFIED

## Config
- TTS: 豆包语音合成2.0 (ArkTTS :8791, zh_male_1)
- HDR: reinhard tonemap
- Audio: loudnorm I=-16, xfade 0.3s, CRF 18
- BGM: 188 首

## 两个项目
- avp: 竖屏 1080×1920 绕线机 → Claude
- cxp: 横屏 1920×1080 工厂动画 → Claude（接管自 Codex，5 scene 已渲染待 concat）

## 创意引擎
- ~/.hermes/skills/avp/industrial-creative-engine/SKILL.md
- 绕线机方向：铜线呼吸(第1) > 线圈禅意 > 精度可见
- 待办：推铜线呼吸给 Claude → Seedance → 出片验证

## 铁律
1. 逆向思维 — 观众想看什么，不是工厂想展示什么
2. 自审计 — 磁盘对账 + 内容审计，不 PASS 不往下走
3. 创意在前 AI 在后 — 不是 AI 决定拍什么
4. Hermes 不执行，只调度 + 审计
5. 不做没派的话，先问再干
6. 别碰 GitHub 写入

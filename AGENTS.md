# Auto Video Platform — Codex 启动必读

> 每次会话开始必读本文件 + shared-context.md
>
> 🔴 历史教训（2026-06-04）：12次迭代全在调GSAP动画，工程化一轮没碰；
> STATUS.md写"PASS"但产出目录是空的；失忆不自学，反复走老路。
> **这3条不改，所有工作白干。**

## 项目定位
制造业AI视频工厂 — ffmpeg实拍素材→LLM脚本→审计→成品宣传片

## 🔴 铁律0：自审计 — 产出不审计等于没做

**任何"完成/跑通/PASS"的声明，必须附带以下证据，缺一不可。**

### 0.1 磁盘对账（防空目录）
```
说"Stage X 产出"时，必须同时贴：
  ls -la output/stageX/   # 文件存在？
  head -3 关键产出文件      # 内容非空？
  ffprobe 核心参数          # 编码/时长/分辨率正确？
  ─────────────────────────────────────
  没有以上3条 → 不算完成，继续修
```

### 0.2 内容审计（防参数好看片子烂）
```
说"final.mp4 可以交付"之前，必须干以下4件事：
  ☐ 打开 script.json 逐条看文案 — 句子是完整的？不是25字硬截断？
  ☐ 问自己：这段文案是看图写的还是套模板的？
  ☐ 对比 script beats 和 roughcut clips — 时间戳对齐了？
  ☐ 问自己：这条片子你自己想转发吗？

  4个 ☐ 没打满 → 闭嘴，继续修
```

### 0.3 不自查 = 白做（历史教训）
```
  ❌ 说"PASS"但目录是空的      → 磁盘对账过了再说话
  ❌ 反复调GSAP不碰工程化      → 每次改动前先问"这是根因还是皮毛"
  ❌ 下个会话忘光上轮教训       → 本文件 + _CONTEXT.md 每次启动必读
  ❌ 知识盲区不问不搜           → 遇到不会的，先检索再问人
```

## 技术栈
- 视频: ffmpeg (libx264/zscale/tonemap/drawtext)
- 视觉分析: 豆包 Seed 1.6 Vision (doubao-seed-1-6-vision-250815) — 唯一可用
- 脚本生成: DeepSeek LLM (deepseek-chat) — 文本only
- 禁止: DeepSeek不支持图片，千问工业画面不准

## 管线架构
```
素材 → Stage1(粗剪) → audit → Stage2(脚本) → audit → Stage3(合成) → audit → 成品
```
每阶段5/5 PASS才放行，任一失败退回重做最多3次。

## 会话启动（每次必做）
1. 读 `D:\auto-video-platform\_CONTEXT.md` — 项目状态快照
2. 读 `~/.codex/shared-context.md` — 团队通信
3. 读本文件 — 死规矩

## 运行命令
```bash
cd D:\auto-video-platform
python pipeline.py 0    # 素材诊断
python pipeline.py 1 D:/隆江视频素材/IMG_034*.MP4   # 粗剪
python pipeline.py 2    # 脚本生成
python pipeline.py 3    # 合成
```

## 关键约束
1. 先粗剪→抽帧→看图→写脚本，不套模板
2. 每步必须审计
3. 素材为iPhone HDR → 必须zscale+tonemap=hable映射
4. 不同设备（绕线机/空压机/水泵）脚本不一样
5. 视觉只用豆包，走 dispatcher.chat(model="doubao-seed-1-6-vision-250815")
6. 共享板 ~/.codex/shared-context.md 每次启动必读

## 已知坑
- CLI默认footage路径乱码（不影响运行）
- 输出目录: output/stage1/ stage2/ stage3/
- 共享板写入被沙箱拦，手动补

## 当前版本
- TTS: 豆包语音合成2.0（ArkTTS，代理 :8791，音色 zh_male_1）
- 脚本模式: content_share（默认）/ viral_short（传 -m）
- 音频: loudnorm I=-16 归一化
- HDR: reinhard tonemap（用户确认）

## 品牌数据
configs/brands/taizhou_longjiang.json — 台州隆江自动化，绕线机

## 会话规则
1. 默认 `python go.py` = 全管线，内容模式（不挂营销组件）
2. 营销脚本加 `-m`：`python pipeline.py 2 -m`
3. 单步：`python pipeline.py [0|1|2|3]`
4. 关键决策写入 `_CONTEXT.md`：`python save_context.py`
5. 不做没派的话，先问再干
6. 别碰 GitHub 写入

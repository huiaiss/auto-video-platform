# Auto Video Platform — 通用AI短视频自动化剪辑平台

## 项目定位

一个**通用的、逆向分析驱动的、全链路AI短视频自动生产平台**。不是为某一个账号或行业定制，而是可配置、可复用、覆盖全行业的工业化视频生产工具。

**一句话**：上传素材 → AI自动分析 → 生成方案 → 输出成品视频 + 多平台发布策略。把一条视频的制作成本从"1个人1天"降到"上传素材等10分钟"。

### 已覆盖的视频类型

| 类型 | 场景 | 状态 |
|------|------|------|
| **AI破绽鉴定**（AI照妖镜） | 科普类，AI生成内容识别教学 | 首个测试用例，全链路跑通中 |
| **企业/工厂宣传** | 真实产线+产品，展现制造实力 | 核心商业场景 |
| **产品展示** | 单品多角度展示+参数讲解 | 电商/外贸企业刚需 |
| **客户案例** | 客户工厂实拍+使用效果+证言 | 信任背书型内容 |
| **技术科普** | 行业知识+技术原理讲解 | 专业IP建设 |

---

## 行业对标与差异化

### 行业主流方案（2025-2026）

| 项目 | 核心思路 | 借鉴点 |
|------|---------|--------|
| **CutClaw** (北交大) | 多智能体：Playwriter→Editor→Reviewer，"假设-验证"循环 | ★★★ 质量审核门控 |
| **ai-mixed-cut** (开源) | 三段式：解构→提取→重构 | ★★★ 解构-重构范式 |
| **Genflow Ad Studio** (Google) | Brand DNA提取→对抗式QC→自校正 | ★★ 品牌合规约束 |
| **OpenReels** (MIT开源) | 6-stage：摄入→理解→叙事→匹配→组装→审核 | ★★★ 全流程自动化 |
| **阿里云IMS** | Timeline JSON驱动→云端渲染 | ★★★ 时间轴驱动架构 |
| **Pictory** (20K+企业) | REST+Webhook，AI提取长视频亮点 | ★★ 企业API设计 |
| **Duix.Avatar** (12K+ stars) | Docker+API：训练+音频+合成 | ★★★ 数字人克隆 |
| **帧导** (自研参考) | 电商拍摄方案生成+四平台分发策略 | ★★★ 多平台发布策略 |

### 我们的差异化

| 维度 | 行业方案 | **我们的方案** |
|------|---------|-------------|
| 内容决策 | 预设模板/人工策划 | **素材逆向分析驱动** — 先扫描再决定 |
| 素材来源 | AI生成或素材库 | **企业真实素材优先** — 实拍润色，不虚构 |
| 质量理解 | LLM笼统评分 | **多维度定量检测** — 清晰度/构图/主体/色彩客观打分 |
| 生产效率 | 单条制作 | **批量参数化** — 同品牌换产品=只换素材 |
| 品牌一致性 | 人工把控 | **Brand DNA锁定** — 一次配置，全局统一 |
| 通用性 | 单一行业 | **配置驱动** — 科普/宣传/产品/培训切换YAML |
| 发布策略 | 只管视频 | **全平台分发** — 抖音/快手/小红书/视频号差异化策略 |
| 运营赋能 | 不管运营 | **爆款方法论内置** — 标题/标签/发布时间/评论运营全覆盖 |
| 本地化 | 英文为主 | **中文全链路原生** — OCR/TTS/字幕/脚本 |

---

## 核心设计理念：逆向开发 (Reverse Development)

传统流程（❌）：
```
确定选题 → 写脚本 → 拍摄/找素材 → 强制匹配 → 反复修改
   ↑________________________________________↓
           浪费大量时间和人力
```

我们的流程（✅）：
```
企业上传素材 → AI全维度扫描 → 亮点自动排序 → 选最佳画面
     → 生成叙事脚本 → TTS配音 → 合成字幕+BGM → 输出专业视频
     → 同时生成：多平台标题/标签/发布时间/封面方案/评论话术
           ↑                                              ↓
           └─── 素材不达标？自动提示具体问题+补拍建议 ───────┘
```

**核心原则**：
1. **素材决定内容** — AI先看有什么，再决定讲什么
2. **机器发现比人预设更客观** — 多维度定量评分，择优使用
3. **自动评分排序** — 每个画面经过清晰度/构图/主体/色彩/稳定性综合打分
4. **闭环自校正** — 关键画面缺失时自动提示补拍，不强行凑合
5. **品牌DNA一次性锁定** — 同企业所有视频自动统一视觉风格
6. **参数化量产** — 同类型视频只替换素材，其他参数全自动继承
7. **发布即运营** — 视频输出同时带多平台发布策略+运营方法论

---

## 平台架构（6层）

```
┌──────────────────────────────────────────────────────────────────┐
│                     Config Layer (配置层)                         │
│  品牌DNA + 视频类型 + 平台策略 + 质量要求                          │
│  全部YAML驱动，零硬编码                                            │
├──────────────────────────────────────────────────────────────────┤
│                  AssetAnalyzer (素材分析层)                        │
│  可插拔检测器，每个检测一个维度，输出0-1标准化分数                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ 清晰度   │ │ 构图     │ │ 主体     │ │ 稳定性   │ │ 色彩   │ │
│  │Sharpness │ │Composition│ │ Subject  │ │Stability │ │ Color  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 人脸/人物│ │ 文字/OCR │ │ 场景分类 │ │ AI破绽   │←可插拔    │
│  │  Face    │ │   Text   │ │  Scene   │ │FlawDetect│           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
├──────────────────────────────────────────────────────────────────┤
│                ScriptGenerator (方案生成层)                        │
│  素材报告 + Brand DNA + 视频类型 → LLM → 完整制作方案              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 叙事脚本 │ │ 分镜表   │ │ BGM推荐  │ │ 后期指南 │          │
│  │Narration │ │Storyboard│ │   BGM    │ │Post Prod │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │ 标题方案 │ │ 标签策略 │ │ 封面方案 │  ← 发布层输入            │
│  │ Titles   │ │  Tags    │ │  Cover   │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
├──────────────────────────────────────────────────────────────────┤
│              CompositionBuilder (视频合成层)                       │
│  结构化方案 + 素材 → Timeline JSON → HyperFrames HTML → MP4       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ TTS配音  │ │ 字幕叠加 │ │ 转场特效 │ │ BGM混音  │          │
│  │ edge-tts │ │ SRT→ASS  │ │Transitions│ │  Audio   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │ 数字人   │ │ 品牌水印 │ │ 封面渲染 │  ← 可选模块             │
│  │ Avatar   │ │ Branding │ │  Cover   │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
├──────────────────────────────────────────────────────────────────┤
│               Publishing Layer (多平台发布层)                      │
│  视频适配 + 发布策略 + 运营方案 + 付费推广                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 抖音策略 │ │ 快手策略 │ │ 小红书   │ │ 视频号   │          │
│  │ 悬念反转 │ │ 老铁文化 │ │图文+视频 │ │ 社交裂变 │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├──────────────────────────────────────────────────────────────────┤
│                  Quality Gate (质量审核层)                         │
│  自动检测 → 自动修复 → 不通过标记 → 人工复核                       │
│  字幕同步 / 音频响度 / 安全区 / 品牌合规 / 内容查重                 │
├──────────────────────────────────────────────────────────────────┤
│                Batch Scheduler (批量调度层)                        │
│  同品牌多产品 → 参数继承 → 并行渲染 → 统一输出                      │
│  GPU队列管理 / 进度追踪 / 失败重试 / 资源回收                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 数据流全景：一条企业视频的完整旅程

```
1. 企业上传素材 → 3张设备图 + 2段产线视频 + 产品参数表
         ↓
2. AssetAnalyzer 扫描：
   · 清晰度检测 → 产线视频2有抖动，标记降级
   · 构图检测 → 设备图2主体偏左，建议居中裁剪
   · 主体检测 → 产线视频1有自动化设备特写，标记为"亮点画面"★
   · OCR提取  → 产品参数表提取关键规格
         ↓
3. ScriptGenerator 基于分析+品牌DNA生成：
   · 脚本：开场3s痛点 → 设备特写15s → 参数5s → CTA 5s
   · 分镜表：5个镜头，含画面/口播/字幕/时长
   · BGM：科技感电子，120BPM，3首推荐曲
   · 后期：剪辑节奏/调色参数/字幕样式/音效建议
   · AI语音：edge-tts zh-CN-YunxiNeural，语速1.05
         ↓
4. CompositionBuilder 合成：
   · TTS生成旁白 → 自动SRT字幕 → 对齐时间轴
   · 应用品牌样式 → 深蓝主色+Logo水印
   · BGM混音 → 人声/BGM/音效分贝平衡
   · HyperFrames渲染 → 1080×1920 MP4
         ↓
5. Publishing Layer 生成发布方案：
   · 抖音：悬念反转标题 + 晚19:00发布 + 千川投流策略
   · 快手：老铁风标题 + 早7:00发布 + 磁力金牛策略
   · 视频号：信任背书标题 + 午12:00发布 + 朋友圈裂变
   · 标签：核心词3个 + 热搜词4个 + 长尾词3个
   · 评论：4条预写评论（引导互动/种草/讨论）
         ↓
6. Quality Gate 审核：
   · 字幕同步 ✓  音频响度-14LUFS ✓
   · 安全区适配 ✓  品牌元素完整 ✓
         ↓
7. 输出：MP4视频 + 多平台发布方案 + 封面图 + 运营指南
```

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| 清晰度检测 | OpenCV (Laplacian variance) | 素材清晰度评分，模糊标记降级 |
| 构图分析 | OpenCV (显著区域 + 三分法) | 主体位置检测，自动裁剪建议 |
| 主体检测 | YOLOv8 / MobileNet SSD | 产品/人物/设备主体识别 |
| 抖动检测 | OpenCV (光流法) | 视频稳定性评分 |
| 色彩分析 | OpenCV (直方图 + 色偏) | 偏色/过曝/欠曝检测 |
| 人脸/人物 | MediaPipe Face Mesh (478点) | 面部特征/表情/占比分析 |
| 手部检测 | MediaPipe Hands (21点) | 手指异常检测（AI破绽专用） |
| OCR文字 | EasyOCR / PaddleOCR (中文) | 素材文字提取，乱码检测 |
| 场景分类 | CLIP / ResNet | 工厂/办公室/户外场景识别 |
| 脚本生成 | Claude API / DeepSeek | 分析报告→结构化方案 |
| TTS配音 | edge-tts (多音色) | 中文配音，支持多种风格 |
| 字幕生成 | whisper.cpp / FFmpeg | 语音→SRT时间轴 |
| 数字人 | Duix.Avatar (Docker+API) | 克隆人+音频驱动口型 |
| 视频渲染 | HyperFrames (HTML+GSAP→MP4) | GPU加速帧精确合成 |
| 视频编码 | FFmpeg (NVENC GPU) | H.264/H.265编码 |
| 封面生成 | Pillow + HTML2Image | 多平台封面自动生成 |

---

## 目录结构

```
auto-video-platform/
├── CLAUDE.md                       # 本文件 — 平台总纲
├── analyzers/                      # 素材分析层
│   ├── base.py                     #   AssetAnalyzer + BaseDetector 基类
│   ├── sharpness_detector.py       #   清晰度检测器
│   ├── composition_detector.py     #   构图分析器
│   ├── subject_detector.py         #   主体检测器
│   ├── stability_detector.py       #   视频抖动检测器
│   ├── color_detector.py           #   色彩/曝光分析器
│   ├── face_detector.py            #   人脸特征检测器 ✅
│   ├── hand_detector.py            #   手部异常检测器 ✅
│   ├── text_detector.py            #   OCR文字检测器 ✅
│   ├── texture_detector.py         #   纹理异常检测器 ✅
│   └── scene_classifier.py         #   场景分类器
├── generators/                     # 方案生成层
│   ├── script_generator.py         #   分析报告→LLM→结构化方案
│   ├── brand_dna.py                #   品牌基因管理
│   ├── tts_builder.py              #   脚本→TTS配音+字幕时间轴
│   ├── bgm_matcher.py              #   情绪→BGM自动匹配
│   ├── title_generator.py          #   多平台标题+标签生成
│   └── cover_designer.py           #   封面图自动生成
├── builders/                       # 视频合成层
│   ├── composition_builder.py      #   方案+素材→HyperFrames HTML
│   ├── timeline_engine.py          #   参数化时间轴引擎
│   ├── subtitle_renderer.py        #   SRT→ASS字幕渲染
│   ├── avatar_integrator.py        #   数字人集成
│   └── templates/                  #   视频风格HTML模板
│       ├── enterprise_promo/       #   企业宣传风格
│       ├── product_showcase/       #   产品展示风格
│       ├── tech_explainer/         #   科技科普风格
│       ├── ai_flaw_detect/         #   AI破绽鉴定风格
│       └── social_proof/           #   客户案例风格
├── publishing/                     # 多平台发布层
│   ├── platform_adapter.py         #   单视频→多平台版本适配
│   ├── publish_strategy.py         #   发布策略生成（时间/频率/互动）
│   ├── paid_promotion.py           #   付费推广方案（千川/金牛/薯条）
│   └── compliance.py               #   各平台合规检查
├── quality/                        # 质量审核层
│   ├── gate.py                     #   质量门控主逻辑
│   └── checks/                     #   检查器
│       ├── subtitle_sync.py        #   字幕与音频同步
│       ├── audio_loudness.py       #   音频响度归一化(-14LUFS)
│       ├── safe_area.py            #   安全区/标题遮挡
│       └── brand_compliance.py     #   品牌合规 + 内容查重
├── scheduler/                      # 批量调度层
│   ├── batch_producer.py           #   参数化批量生产
│   └── gpu_queue.py                #   GPU渲染队列
├── configs/                        # 配置中心
│   ├── brands/                     #   品牌DNA配置
│   ├── video_types/                #   视频类型模板
│   └── platform.yaml               #   平台全局配置
├── models/                         # AI模型
│   └── download_models.py
└── tests/
```

---

## 配置体系

### 1. 视频类型配置

```yaml
# configs/video_types/enterprise_promo.yaml
type: "enterprise-promo"
description: "企业/工厂宣传视频"

asset_analysis:
  detectors:
    - sharpness
    - composition
    - subject
    - color
    - stability
  min_acceptable_score: 0.5
  highlight_threshold: 0.75     # 自动标记亮点画面

style:
  resolution: "1080x1920"
  fps: 30
  background: "linear-gradient(135deg, #0a1628, #1a2a4a)"
  accent_color: "#00a8ff"
  font_title: "Noto Sans SC Bold"
  font_body: "Noto Sans SC"
  subtitle_style: "outline"

voice:
  engine: "edge-tts"
  voice: "zh-CN-YunxiNeural"
  speed: 1.05

structure:
  hook: 3s          # 开场钩子
  showcase: 15s     # 核心展示
  features: 8s      # 卖点参数
  proof: 7s         # 信任背书
  cta: 5s           # 行动引导

platforms:
  douyin:
    title_style: "悬念反转"      # 标题风格
    best_times: ["19:00", "12:00", "21:00"]
    hashtags: ["#自动化设备", "#智能工厂"]
    duration_range: [25, 55]     # 秒
  kuaishou:
    title_style: "接地气提问"
    best_times: ["07:00", "19:00"]
    duration_range: [30, 57]
  xiaohongshu:
    title_style: "干货教程"
    generate_image_post: true    # 同时生成图文笔记
  shipinhao:
    title_style: "信任背书"
    social_sharing_hook: true    # 朋友圈转发引导

quality_gate:
  subtitle_sync_tolerance: 0.2s
  audio_loudness_target: -14LUFS
  min_resolution: 720p
  required_brand_elements:
    - logo_watermark
    - company_name_endcard
```

### 2. AI破绽鉴定配置（首个测试用例）

```yaml
# configs/video_types/ai_flaw_detect.yaml
type: "ai-flaw-detect"
description: "AI内容破绽鉴定科普视频"

asset_analysis:
  detectors:
    - hand           # 手指异常（6指/粘连）
    - face           # 面部不对称
    - text           # 文字乱码
    - texture        # 纹理塑料感
  flaw_threshold: 0.5   # 低于此分不展示

style:
  background: "radial-gradient(#0d1b2a, #06060b)"
  accent_color: "#00e676"
  highlight_style: "pulse_circle"   # 脉冲圆圈标注
  resolution: "1080x1920"

voice:
  engine: "edge-tts"
  voice: "zh-CN-YunxiNeural"
  speed: 1.1

structure:
  hook: 3s       # "这张图看起来正常对吧？放大后..."
  reveal: 20s    # 逐处标注破绽（红色圆圈+说明）
  compare: 10s   # 真vs假对比
  summary: 10s   # 知识点总结
  outro: 7s      # "关注AI照妖镜，下次被骗的不是你"

platforms:
  douyin:
    title_templates:
      - pattern: "AI又翻车了！这次是{flaw_type}"
      - pattern: "{count}秒识别AI假图的第{trick_num}招"
      - pattern: "这张图里有一个致命破绽，你发现了吗"
    hashtags: ["#AI照妖镜", "#AI识别", "#防骗指南"]
```

### 3. Brand DNA 配置

```yaml
# configs/brands/taizhou_longjiang.yaml
brand: "台州隆江自动化设备"
industry: "自动化设备制造"
tagline: "让绕线更智能"

visual_identity:
  primary_color: "#0057b8"
  secondary_color: "#00a8ff"
  logo_path: "/assets/brands/longjiang/logo.png"
  font_family: "Noto Sans SC"

voice_identity:
  tts_voice: "zh-CN-YunxiNeural"
  tone: "专业、可靠、技术领先"
  banned_words: ["便宜", "低价", "最简单"]

content_rules:
  must_mention: ["无刷电机绕线机", "自动排线", "精密张力控制"]
  competitor_blur: true

output:
  default_platform: "douyin"
  hashtags: ["#自动化设备", "#绕线机", "#智能工厂"]
```

---

## 多平台发布策略体系

### 四大平台差异化

| 维度 | 抖音 | 快手 | 小红书 | 视频号 |
|------|------|------|--------|--------|
| **标题风格** | 口语化+悬念反转 | 接地气+老铁提问 | 精致干货+SEO关键词 | 信任背书+情感共鸣 |
| **最佳时长** | 25-55s | 30-57s | 30-60s + 图文 | 30-60s |
| **发布时间** | 19:00-22:00 | 07:00/19:00-22:00 | 12:00/20:00 | 12:00/20:00 |
| **封面比例** | 3:4 竖图 | 1:1 方图 | 3:4 竖图 | 1:1 或 16:9 |
| **标签策略** | 3-5个精准标签 | 封面标题大字 | 核心词+场景词+长尾词 | @提及+话题绑定 |
| **互动方式** | 首发自评引导讨论 | 老铁式接地气互动 | 收藏+评论双驱动 | 朋友圈裂变+私域导流 |
| **投流工具** | 巨量千川·全域推广 | 磁力金牛·全站推广 | 薯条测款→聚光放量 | ADQ+微信豆 |
| **核心算法** | 停留时长+互动密度 | 粉丝黏性+社交互动 | 内容质量+SEO搜索 | 社交关系链裂变 |
| **合规要点** | 禁用绝对化用语 | 接地气但不低俗 | 严禁站外导流 | AI内容必须标注 |

### 标题生成引擎

内置6种钩子类型，按平台+行业自动匹配：

| 钩子类型 | 适用场景 | 示例 |
|----------|---------|------|
| **悬念好奇** | 科普/测评 | "这张图放大3倍后，我发现了一个诡异的地方" |
| **反差对比** | 产品/案例 | "同行还在手工作业，他们已经全自动了" |
| **身份认同** | 行业/职业 | "做制造业的都懂，这个参数意味着什么" |
| **痛点解决** | 功能/卖点 | "每天绕线1000个？这个设备让你提前下班" |
| **视觉冲击** | 展示/颜值 | "这就是工业美学的天花板" |
| **反常识** | 科普/技术 | "90%的人不知道，自动化设备也需要AI校准" |

### 封面自动生成

```
输入：视频标题 + 品牌DNA + 平台规格
输出：多平台封面图（自动适配尺寸+配色+字体）
- 抖音：3:4 竖版，品牌色+大字标题+视觉锚点
- 快手：1:1 方版，标题占封面上1/3
- 小红书：3:4 竖版，精致排版+多图拼接
- 视频号：1:1 方版，信任元素突出
```

### 运营方法论内置

每套方案自动附带：
- **发布时间建议**：按账号粉丝画像给最佳时段
- **首发评论**：引导互动的自评话术
- **评论区运营**：4条预写评论（引导转化/增加互动/触发讨论/隐藏种草）
- **热点借势**：当前季节/节日可结合的营销切入点
- **付费推广**：冷启动预算/定向策略/出价建议/ROI优化（分新手/成熟账号）

---

## 检测器接口标准

```python
class BaseDetector(ABC):
    name = "base"  # 唯一标识

    @abstractmethod
    def detect(self, asset_path: str) -> list[dict]:
        """
        分析素材文件。
        
        Returns:
            list of findings, each with:
            - type: str       # 发现类型
            - desc: str       # 中文描述
            - score: float    # 0-1 归一化分数
            - severity: str   # "high" | "medium" | "low"
            - cx: int         # 中心x坐标
            - cy: int         # 中心y坐标
            - details: str    # 详细说明
        """
```

评分约定：
- **质量类检测器**（清晰度/构图/色彩）：score越高=质量越好（0=不可用, 1=完美）
- **缺陷类检测器**（AI破绽/抖动）：score越高=问题越严重（0=正常, 1=明显异常）
- `AssetAnalyzer` 统一处理两种方向，最终输出 `highlight_score`（值得展示的分数）

**已实现**：FaceDetector, HandDetector, TextureDetector, TextDetector
**待实现**：SharpnessDetector, CompositionDetector, SubjectDetector, StabilityDetector, ColorDetector, SceneClassifier

---

## 开发路线图

### Phase 1：核心引擎 — 素材分析 ✅（基本完成）
- [x] AssetAnalyzer + 可插拔检测器框架
- [x] FaceDetector (面部不对称/眼睛/嘴巴)
- [x] HandDetector (手指粘连/比例/关节)
- [x] TextureDetector (纹理塑料感/拼接痕)
- [x] TextDetector (OCR乱码识别)
- [ ] SharpnessDetector + CompositionDetector
- [ ] 视频帧提取+逐帧分析管线
- [ ] 跨检测器评分归一化标准

### Phase 2：方案生成 — 脚本+配音+发布策略
- [ ] BrandDNA Manager
- [ ] ScriptGenerator (分析报告→LLM→结构化方案)
- [ ] TitleGenerator (多平台标题+标签+封面方案)
- [ ] TTSBuilder (脚本→TTS+SRT时间轴)
- [ ] BGMMatcher (情绪→BGM自动匹配)
- [ ] 配置驱动的视频类型系统

### Phase 3：视频合成 — Timeline→MP4
- [ ] TimelineEngine (参数化时间轴)
- [ ] CompositionBuilder (方案+素材→HyperFrames HTML)
- [ ] 5套视频风格模板
- [ ] SubtitleRenderer (SRT→ASS渲染)
- [ ] 品牌水印/Logo叠加自动化

### Phase 4：发布+质量 — 企业级量产
- [ ] PlatformAdapter (单视频→四平台版本)
- [ ] PublishStrategy 生成器
- [ ] PaidPromotion 方案生成
- [ ] QualityGate 自动审核+AutoFix
- [ ] BatchScheduler 参数化批量生产

### Phase 5：高级功能
- [ ] Duix.Avatar 数字人克隆集成
- [ ] 多平台一键发布API
- [ ] 数据看板（视频表现/生产效率/素材复用率）

---

## 关键设计决策

1. **素材分析永远在前** — 不预设脚本，一切由素材实际分析结果驱动
2. **检测器独立可插拔** — 新增检测维度不影响已有功能
3. **评分标准化** — 所有检测器输出0-1分数，跨类型可比
4. **闭环自校正** — 素材不达标时提示具体问题+补拍建议
5. **配置驱动，零硬编码** — 换视频类型/品牌/平台只需换YAML
6. **中文全链路原生** — OCR/TTS/字幕/脚本全中文
7. **品牌DNA一次性锁定** — 同企业所有视频自动统一风格
8. **参数化量产** — 换产品=只换素材+产品名
9. **真实素材优先** — 企业实拍，AI润色，不虚构
10. **视频+发布方案同出** — 不只做视频，附带全套运营方案
11. **从企业主视角设计** — 零学习成本，上传素材→等结果→发布
12. **AI照妖镜是验证全链路的首个测试用例**，不是唯一产品

---

## 企业主视角的产品体验

作为自动化设备工厂老板，我对这款工具的要求：

1. **零学习成本**：上传照片+视频，点按钮，视频+发布方案一起出来
2. **保持真实**：用的是我工厂实拍，客户看到真实产线
3. **看起来专业**：品牌统一、配音专业、字幕准确、比我自己拍强10倍
4. **速度快**：今天拍新设备，今天出视频发抖音
5. **批量做**：10款设备一次上传，批量出片
6. **能改能调**：不满意说一句"配音太慢"就能改
7. **不只做视频**：标题怎么写、什么时候发、封面怎么做、评论怎么回，都告诉我
8. **数据能看**：哪些视频效果好，哪个素材复用最多
9. **成本可控**：比养剪辑团队便宜，比外包公司响应快
10. **多平台通吃**：抖音/快手/视频号/小红书/B站，一个素材全适配

# 帧导 — 多Agent协同工作室架构

## 核心思维转变

```
传统管线思维:                       Agent协同思维:
                                    
A → B → C → D (数据流过固定管道)     总导演(我) ←→ 多个专业Agent
                                     ├→ 产品分析师
出了问题只能从头跑                    ├→ 创意总监  
                                     ├→ 场景设计师
                                     ├→ 脚本编剧
                                     ├→ BGM总监
                                     ├→ 配音演员
                                     ├→ 摄影师
                                     ├→ 剪辑师
                                     ├→ 质检师
                                     ├→ 竞品情报员
                                     └→ 策略师
                                         ↑
                              并行协作 / 互相评审 / 随时退回重做
```

---

## 一、角色体系：12个专业Agent

### 🧠 我是总导演（Director）

我不写代码，我做决策：

| 职责 | 具体动作 |
|------|---------|
| **任务分解** | 老板说"给这双鞋做套内容" → 拆成分析/创意/场景/脚本/BGM/出图/出片/策略8个子任务 |
| **Agent调度** | 决定哪些Agent并行、哪些串行（场景设计师和脚本编剧可以同时开工） |
| **质量把关** | 每个Agent交活 → 我审核 → 通过或退回 |
| **跨Agent协调** | 发现脚本和场景风格不一致 → 召集两个Agent对齐 |
| **最终决策** | 质检师说60分不够 → 我决定重做还是降级接受 |
| **交付确认** | 所有输出到位 → 我最终看一眼 → 交付 |

### 12个专业Agent

#### 1. 🎯 产品分析师 Agent
```
输入: 8-10张产品实拍图
能力:
  - 品类识别（老爹鞋/玛丽珍/乐福鞋/马丁靴...）
  - 风格关键词提取（复古/潮流/韩系/街头...）
  - 材质识别（网面/皮质/绒面/反光...）
  - 色彩分析（主色+辅色+hex推测）
  - 受众画像（性别/年龄/消费力/场景）
  - 卖点提炼（厚底增高/透气网面/百搭设计...）
  - 设计亮点标注（logo位置/拼接方式/特殊纹理）
工具: Doubao Vision API + OpenCV色彩分析 + 鞋类知识库
输出: 结构化产品分析JSON
质量自检: 品类是否在鞋类知识库中存在？颜色hex是否合理？受众是否和品类匹配？
```

#### 2. 🎨 创意总监 Agent
```
输入: 产品分析JSON + 行业知识库
能力:
  - 创意概念命名（"城市漫游者"/"午后慢时光"/"步履时光"）
  - 概念故事写作（一句话：在什么地方/什么情绪/什么氛围）
  - 2-3个场景设计（每个包含：场景名/描述/为什么适合/拍摄建议）
  - 配色方案（primary/secondary/accent + 理由）
  - 模特穿搭方向（服装/姿势/不露脸）
  - 构图风格建议（低角度仰拍/平视特写/跟随镜头）
  - 差异化定位（和同类产品的不同点）
  - BGM方向建议（BPM/曲风/情绪）
  - 钩子类型推荐（身份认同/反常识/数字痛点...）
工具: DeepSeek Chat + 鞋类知识库 + 爆款钩子库 + BGM知识库
输出: CreativeBrief JSON
质量自检: 场景是否和产品品类匹配？配色是否真实反映产品颜色？概念名是否独特？
```

#### 3. 🏞️ 场景设计师 Agent
```
输入: 创意简报中的场景描述 + 配色方案
能力:
  - 根据"窗边休闲午后"描述生成场景背景图
  - 色调自动匹配创意配色方案
  - 光影方向根据场景描述调整
  - 输出多分辨率（1600x1600 / 2000x2000）
  - 确保背景有明确的层次（墙壁/地板/前景）
工具: AI生图API（即梦Seedream / ComfyUI / 程序化纹理降级）
输出: 场景背景PNG列表
质量自检: 分辨率≥1600px？色调和配色方案一致(ΔE<15)？文件有效(>1KB)？CLIPScore与描述≥0.3？
```

#### 4. ✍️ 脚本编剧 Agent
```
输入: 产品分析JSON + 创意简报
能力:
  - 写标题（3-5个版本，覆盖不同钩子类型）
  - 写hook（开场3-5秒抓注意力）
  - 写7个beat口播（每个15-25字，对应不同情绪/动画）
  - 写outro（结尾CTA，引导行动）
  - 每个beat标注：时长/情绪/动画类型/画面描述
  - L2备选文案（更口语/更短版本）
  - 总时长控制在25-55秒（抖音推荐）
工具: DeepSeek Chat + 情绪弧线模板 + 爆款脚本结构
输出: Script (title + beats[] + outro)
质量自检: 总时长在25-55s？每个beat有情绪标注？开场3秒有钩子？CTA有明确行动指令？
```

#### 5. 🎵 BGM音乐总监 Agent
```
输入: 创意简报中的情绪关键词 + BPM范围
能力:
  - 从BGM知识库匹配3-5首
  - 给出选择理由（为什么这首适合这个情绪）
  - 标注版权状态（免费/需购买/CC协议）
  - 如果需要，生成BGM搜索关键词
工具: BGM知识库 (bgm_knowledge.py) + 版权音乐API
输出: BGM推荐列表 [{name, url, bpm, genre, license, reason}]
质量自检: BPM在建议范围内？曲风匹配情绪？有至少1个免费选项？
```

#### 6. 🎙️ 配音演员 Agent
```
输入: 脚本文字
能力:
  - TTS语音合成（中文，多音色可选）
  - 语速控制（1.0-1.3x）
  - 情感标记处理（开心/严肃/兴奋对应的语速微调）
  - SRT字幕自动生成（时间轴对齐）
  - 输出MP3 + SRT双文件
工具: edge-tts (多音色) + Azure TTS + SRT生成
输出: narration.mp3 + subtitles.srt
质量自检: MP3可播放？时长和脚本一致？SRT时间轴无跳跃？音频响度约-14LUFS？
```

#### 7. 📷 摄影师 Agent
```
输入: 产品图(多角度) + 场景背景图 + 创意简报 + 平台尺寸列表
能力:
  - rembg抠图（保留阴影/边缘精细）
  - 多场景合成（每张产品图 × 每个场景 = 多张套图）
  - 六平台尺寸适配（淘宝800×800 / 抖音3:4 / 京东白底...）
  - 批量输出（场景数 × 角度数 × 平台数 ≥ 80张）
  - 自动命名（产品_场景_角度_平台.png）
工具: rembg + Pillow + 平台尺寸模板
输出: output/images/ 目录下的80+张PNG
质量自检: Amazon白底RGB(255,255,255)±5？产品占比≥85%？分辨率≥2000px长边？无抠图残边？
```

#### 8. 🎬 剪辑师 Agent
```
输入: Script + TTS音频 + SRT字幕 + BGM + 素材清单 + 创意简报
能力:
  - 为每个beat选择最合适的电商组件（6组件库）
  - 组装HyperFrames HTML（GSAP时间轴）
  - 注入品牌色（--brand-primary等CSS变量）
  - 时间轴对齐（口播/字幕/动画/BGM四轨同步）
  - Chromium录制 + FFmpeg混流 → MP4
  - 输出1080×1920竖版视频
工具: CompositionBuilder + AssemblyEngine + ChromiumRenderer + FFmpeg
输出: output/videos/index.html + output.mp4
质量自检: 分辨率1080×1920？帧率30fps？GSAP时间轴无丢帧？6个电商组件全部渲染？
         TTS同步偏差≤0.2s？音频响度-14LUFS？品牌色正确注入？
```

#### 9. 🔍 质检师 Agent
```
输入: 所有Agent的输出
能力:
  - 7维结构评分（STRUCTURE/L1_SCRIPT/L2_SCRIPT/SCENE_TIER/PERSPECTIVE/COMPLIANCE/HOOK）
  - 图片质量检查（分辨率/白底/占比/CLIPScore/边缘）
  - 视频质量检查（分辨率/帧率/响度/组件完整性/TTS同步）
  - 文案合规检查（禁用词/品牌名正确/无虚构）
  - 输出QA报告：通过/需修改/拒绝
工具: gatekeeper + CLIP + FFprobe + pyloudnorm + 规则引擎
输出: QAReport {pass, score, issues[], suggestions[]}
质量自检: 所有维度都检查了？每个issue有具体修复建议？
```

#### 10. 🕵️ 竞品情报员 Agent
```
输入: 竞品平台列表 + 任务上下文
能力:
  - 爬取即梦/Vali/潮际好麦等竞品最新动态
  - 价格对比矩阵
  - 功能差距分析
  - 质量基准测试（下载竞品demo → CLIPScore对比）
  - 输出情报简报 + 策略建议
工具: WebFetch + 数据解析 + 竞品数据库
输出: IntelBrief {threat_level, key_findings, recommendations}
质量自检: 数据来源可追溯？对比维度公平？建议可执行？
```

#### 11. 📢 策略师 Agent
```
输入: 产品分析 + 创意简报 + 脚本
能力:
  - 四平台标题方案（抖音/快手/小红书/视频号）
  - 标签策略（核心词+热搜词+长尾词）
  - 发布时间建议（按平台+受众画像）
  - 封面方案（尺寸+配色+文字）
  - 4条预写评论（引导互动/种草/讨论/隐藏转化）
  - 付费推广建议（千川/金牛/薯条预算+定向）
工具: DeepSeek Chat + 平台规则库 + 发布时间数据库
输出: PublishingStrategy
质量自检: 每个平台都有标题？标签3-5个？发布时间符合平台规律？封面尺寸正确？
```

#### 12. 📋 交付经理 Agent
```
输入: 所有最终输出文件
能力:
  - 整理目录结构
  - ZIP打包
  - 生成交付清单（列出所有文件+用途+质量标准）
  - 归档到历史记录
  - 输出老板可看的摘要
工具: Python zipfile + 文件系统 + 模板
输出: deliverable.zip + DELIVERY.md
质量自检: 所有文件可打开？ZIP不损坏？清单完整？
```

---

## 二、协作协议

### 任务分发格式

总导演给每个Agent发任务时，使用统一格式：

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "director",
  "to": "script_writer",
  "task_type": "generate",
  "priority": "high",
  "payload": {
    "product_analysis": { "... 产品分析JSON ..." },
    "creative_brief": { "... 创意简报JSON ..." },
    "requirements": {
      "beat_count": 7,
      "total_duration_s": [25, 55],
      "platform": "douyin",
      "hook_types": ["身份认同", "反常识"]
    }
  },
  "context": {
    "brand": "凯妮芬",
    "product_name": "复古厚底老爹鞋",
    "previous_feedback": null
  }
}
```

### 成果交付格式

Agent完成任务后交回：

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "script_writer",
  "to": "director",
  "status": "completed",
  "output": {
    "script": { "... Script JSON ..." },
    "files": ["output/scripts/script_v1.json"]
  },
  "self_review": {
    "score": 85,
    "issues": [],
    "notes": "beat3和beat5的情绪过渡可能需要调整"
  },
  "need_review_from": ["creative_director"]
}
```

### 退回修正格式

总导演不满意时：

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "director",
  "to": "script_writer",
  "task_type": "revise",
  "issues": [
    {
      "field": "beats[2].text",
      "problem": "beat3文案太长（32字），抖音口播建议15-25字",
      "suggestion": "拆成两句，或者精简到20字以内"
    }
  ],
  "context": {
    "original_output": { "... 之前的Script ..." }
  }
}
```

### 跨Agent同行评审

创意总监可以评审脚本编剧的输出：

```json
{
  "from": "creative_director",
  "to": "script_writer",
  "type": "peer_review",
  "verdict": "approved_with_suggestions",
  "strengths": ["hook抓人", "beat2情绪到位"],
  "suggestions": ["beat5可以更强调舒适感，和创意概念的'轻盈'对齐"]
}
```

---

## 三、总导演调度流程

### 标准任务：老板上传一双鞋的8张图

```
PHASE 0: 任务接收
─────────────────────────────────────────────
Director: 收到任务。验证输入（≥3张图？格式OK？）
         → 通知竞品情报员：开始后台收集同类产品数据
         
PHASE 1: 产品分析 (必须第一步)
─────────────────────────────────────────────
Director → 产品分析师: "分析这双鞋"
产品分析师 → Director: ProductAnalysis JSON
Director 审核: 品类准确？风格标签够？颜色hex合理？
  ├─ 通过 → 继续
  └─ 不通过 → 退回重做（附具体问题）

PHASE 2: 创意+脚本+场景 (可以并行!)
─────────────────────────────────────────────
Director → 创意总监: "基于产品分析生成创意"
         → (并行，不依赖创意结果)
         
创意总监 → Director: CreativeBrief JSON
Director 审核: 概念独特？场景匹配？模特穿搭具体？
  ├─ 通过 → 进入PHASE 3
  └─ 不通过 → 退回

PHASE 3: 内容工厂 (并行启动)
─────────────────────────────────────────────
Director → 脚本编剧: "写7 beat口播脚本"
         → 场景设计师: "生成3个场景背景图"
         → BGM总监: "匹配合适的BGM"
         → (三个Agent同时开工!)
         
脚本编剧 → Director: Script JSON
场景设计师 → Director: 3张场景背景PNG
BGM总监 → Director: BGM推荐列表

Director 交叉审核:
  ├─ 脚本和场景的情绪一致？
  ├─ BGM的节奏和脚本的beat节点对齐？
  └─ 所有输出和创意简报的concept一致？
  
任一不通过 → 退回对应Agent重做

PHASE 4: TTS + 素材 (串行-依赖脚本)
─────────────────────────────────────────────
Director → 配音演员: "合成TTS语音"
配音演员 → Director: narration.mp3 + subtitles.srt

PHASE 5: 出图+出片 (并行!)
─────────────────────────────────────────────
Director → 摄影师: "批量合成80+张套图"
         → 剪辑师: "组装HTML+渲染MP4"
         → (两个Agent同时开工!)
         
摄影师 → Director: 80+张PNG (六平台)
剪辑师 → Director: MP4视频

PHASE 6: 质检 (全部输出到位后)
─────────────────────────────────────────────
Director → 质检师: "检查所有输出"
质检师 → Director: QAReport

Director 决策:
  ├─ score ≥ 85 → 通过，进入交付
  ├─ score 70-84 → 看具体问题，轻微问题→修复，严重问题→退回
  └─ score < 70 → 退回问题最大的Agent重做

PHASE 7: 策略+交付 (质检通过后)
─────────────────────────────────────────────
Director → 策略师: "生成四平台发布方案"
         → 交付经理: "打包所有文件"
         
策略师 → Director: PublishingStrategy
交付经理 → Director: deliverable.zip

PHASE 8: 最终交付
─────────────────────────────────────────────
Director 最终审核 → 交付给老板
竞品情报员后台数据 → 存入知识库供下次使用
```

### 总时间对比

```
传统管线: A(30s) → B(30s) → C(20s) → D(15s) → E(60s) → F(120s) → G(30s)
         = 305秒 (5分钟)

Agent协同: 
  Phase 1: 产品分析 30s
  Phase 2-3: 创意+BGM(并行) 30s + 场景+脚本(并行) 30s = 30s
  Phase 4: TTS 15s
  Phase 5: 出图+出片(并行!) 120s
  Phase 6: 质检 30s
  Phase 7: 策略+交付(并行) 15s
  = 240秒 (4分钟)

关键增益不是时间，是质量:
  - 每个环节有独立的专业Agent把关
  - 创意/脚本/场景可以互相校对
  - 质检不是最后一道，而是每道都自检
  - 出了问题只需退回一个Agent，不用重跑全链路
```

---

## 四、Agent能力矩阵

| Agent | 类型 | 工具 | 可并行? | 关键依赖 |
|-------|------|------|---------|---------|
| 产品分析师 | 视觉分析 | Doubao Vision, OpenCV | 独立 | 无 |
| 创意总监 | 创意推理 | DeepSeek Chat, 知识库 | 依赖分析结果 | 产品分析 |
| 场景设计师 | 图像生成 | AI生图API, 纹理引擎 | 独立 | 创意简报 |
| 脚本编剧 | 文字创作 | DeepSeek Chat, 钩子库 | 独立 | 产品分析+创意 |
| BGM总监 | 匹配推荐 | BGM知识库, 音乐API | 独立 | 创意简报 |
| 配音演员 | TTS合成 | edge-tts, Azure TTS | 依赖脚本 | Script |
| 摄影师 | 图像处理 | rembg, Pillow, 尺寸模板 | 独立 | 场景图+产品图 |
| 剪辑师 | 视频组装 | CompositionBuilder, Chromium | 独立 | Script+TTS+BGM |
| 质检师 | 质量检查 | gatekeeper, CLIP, FFprobe | 依赖所有输出 | 所有Agent输出 |
| 竞品情报员 | 数据收集 | WebFetch, 数据解析 | 独立(后台) | 无 |
| 策略师 | 方案生成 | DeepSeek Chat, 平台规则库 | 独立 | 脚本+创意 |
| 交付经理 | 文件管理 | zipfile, 模板 | 独立 | 所有最终输出 |

---

## 五、实施路径

### 阶段1: Agent骨架 (本周)

为每个Agent创建独立的定义文件：

```
auto-video-platform/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # Agent基类
│   ├── director.py             # 总导演 (我)
│   ├── product_analyst.py      # 产品分析师
│   ├── creative_director.py    # 创意总监
│   ├── scene_designer.py       # 场景设计师
│   ├── script_writer.py        # 脚本编剧
│   ├── bgm_director.py         # BGM总监
│   ├── voice_actor.py          # 配音演员
│   ├── photographer.py         # 摄影师
│   ├── video_editor.py         # 剪辑师
│   ├── qa_inspector.py         # 质检师
│   ├── intel_agent.py          # 竞品情报员
│   ├── strategist.py           # 策略师
│   └── delivery_manager.py     # 交付经理
├── agents/
│   ├── protocols.py            # Agent间通信协议
│   ├── task_queue.py           # 任务队列管理
│   └── context_bus.py          # 上下文共享总线
```

### 阶段2: Agent实现 (1-2周)

每个Agent是一个独立可运行的单元：
- `base_agent.py`: Agent基类，定义标准接口
  - `receive_task(task_json)` → 接收任务
  - `execute()` → 执行
  - `deliver()` → 交付结果
  - `self_review()` → 自检
  - `accept_feedback(feedback)` → 接收修正意见
- 每个Agent继承基类，实现自己的 `execute()` 逻辑
- Agent可以调用现有的 services/ builders/ 模块

### 阶段3: 协同编排 (2-3周)

Director的编排逻辑：
- 解析老板需求 → 生成任务DAG
- 按依赖关系决定串行/并行
- 监听每个Agent的交付
- 审核 → 通过/退回
- 最终聚合 → 交付

```python
class Director:
    def handle_request(self, request: UserRequest) -> FinalDelivery:
        # 1. 拆解任务
        tasks = self.decompose(request)
        
        # 2. 构建依赖图
        dag = TaskDAG(tasks)
        
        # 3. 并行调度
        results = {}
        for batch in dag.parallel_batches():
            batch_results = self.dispatch_batch(batch)
            for r in batch_results:
                if not self.review(r):
                    # 退回重做
                    batch_results[r.agent] = self.request_revision(r)
            results.update(batch_results)
        
        # 4. 质量把关
        qa = self.agents['qa_inspector'].review(results)
        if qa.score < 70:
            # 找到最差的Agent，退回重做
            worst = qa.worst_performer()
            results[worst] = self.request_revision(results[worst])
        
        # 5. 打包交付
        return self.agents['delivery_manager'].package(results)
```

### 阶段4: 竞品情报Agent常驻 (持续)

竞品情报员作为后台Agent持续运行：
- 项目开始时自动启动
- 周期性收集数据
- 其他Agent在做决策时可以查询情报
- 每周自动生成简报

---

## 六、和现有管线的关系

```
旧架构 (Pipeline): 保留为Agent的工具层
─────────────────────────────────────────
services/creative_engine.py  → 产品分析师Agent 调用它
builders/composition_builder.py → 剪辑师Agent 调用它
builders/assembly_engine.py  → 剪辑师Agent 调用它
builders/components_ecommerce.py → 剪辑师Agent 调用它
generators/script_generator.py  → 脚本编剧Agent 调用它
generators/tts_builder.py       → 配音演员Agent 调用它
services/image_processor.py     → 摄影师Agent 调用它
services/gatekeeper.py          → 质检师Agent 调用它

新架构 (Agents): 覆盖在管线之上
─────────────────────────────────────────
agents/ 目录是新的"大脑层"
旧代码是"手脚层"
大脑做决策，手脚执行
```

---

## 七、核心优势

| 维度 | 旧管线 | Agent工作室 |
|------|--------|------------|
| 质量 | 最后一道质检，出问题要重跑全链路 | 每个Agent自检+交叉审核+总导演把关 |
| 效率 | 全串行，一个卡住全停 | 能并行的并行，只退回有问题的Agent |
| 灵活 | 固定流程，换行业重写 | 换行业=换知识库，Agent框架不变 |
| 可解释 | 黑盒，出错不知道哪个环节 | 每个Agent有独立输出，责任清晰 |
| 进化 | 改一处可能影响全链路 | Agent独立升级，接口不变 |
| 竞品感知 | 没有 | 竞品情报员持续提供外部视角 |
| 创意独特性 | LLM一次生成，没有反复打磨 | 创意总监+脚本编剧+场景设计师三方对齐 |

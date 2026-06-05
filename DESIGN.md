# Auto Video Platform — 制造业实体商家的AI询盘工厂

> Hermes 战略分析：2026-05-25 | 定位修正版 v2：2026-06-04
> 
> **定位变更：从"视频工厂"改为"询盘工厂"。**
> 出视频是手段，不是目的。目的是客户收到询盘。
> 数据支撑：追马网帮阀门厂 3 个月 800 条询盘，靠的不是视频质量，是"发布→被搜到→留资→跟进"整条链路。

## 项目定位

**不是"又一个剪映"，不是"通用AI视频工具"。**

**是：制造业实体商家的AI询盘工厂。** 目标客户是工厂老板、设备厂家、实体门店——他们手上有设备素材但不会做视频，更不会把视频变成询盘。本平台帮他们：上传素材 → AI自动分析机器亮点 → 生成专业宣传视频 → 四平台差异化发布 → GEO数据让AI搜索能搜到 → 落地页转化留资 → 客户收到询盘。

**核心逻辑**："老板自己用了有效，他们就敢买。" —— 隆江绕线机是第一只验证品。

**一句话**：给设备拍段视频 → AI看懂是什么机器、亮点在哪里 → 10分钟出宣传片。

### 目标客户画像

| 客户类型 | 典型需求 | 痛点 |
|---------|---------|------|
| **自动化设备厂**（数控机床、绕线机、注塑机） | 展示机器运行、精度、产能 | 机器在动，不知道拍哪个角度 |
| **工厂/代工厂** | 展示产线规模、品控能力 | 想接外贸单，没有像样视频 |
| **实体门店**（汽修、门窗、家具） | 展示手艺、设备、案例 | 只会用抖音拍15秒 |
| **外贸/跨境电商** | 产品多角度展示+参数+证书 | 国外客户要视频，找人拍太贵 |

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

---

## 反同质化设计体系（核心架构决策）

> ⚠️ 模板化 = 同质化 = 死路。这条必须刻在架构骨头上。

### 设计原则

```
模板是骨架  → 决定视频的"功能正确"（开场→展开→收尾）
Brand DNA   → 决定视频的"视觉身份"（配色/字体/Logo/转场风格）
叙事引擎    → 决定视频的"内容角度"（8+种叙事视角智能选择）
素材驱动    → 决定视频的"随机变异"（素材不同=决策不同=成品不同）
```

**骨架通用，血肉差异化。** 同一个绕线机视频模板 → 套不同Brand DNA → 选不同叙事角度 → 用不同素材 → 百万级组合空间 → 几乎不可能撞车。

---

### 三刀砍同质化

#### 🔪 第一刀：Brand DNA → 视觉上就不同

两套完整的 Brand DNA 配置，同一段素材进去，出来两条"看起来完全不同"的视频：

```yaml
# 隆江绕线机
brand_dna:
  color_primary: "#C8102E"    # 隆江红 — 品牌主色
  color_accent: "#FFD700"     # 金色点缀
  font_primary: "思源黑体 Bold"
  font_secondary: "思源宋体"
  logo: "longjiang_logo.png"
  logo_position: "bottom-right"
  logo_opacity: 0.15           # 水印式，不抢戏
  transition_style: "hard_cut" # 工业感，干净利落
  lower_third_style: "参数条-科技蓝底"
  bgm_genre: ["industrial_tech", "orchestral"]
  narration_style: "专业稳重"   # 数据说话
  color_grading: "金属质感"
```

```yaml
# 另一家绕线机厂（假设的竞品客户）
brand_dna:
  color_primary: "#0066CC"    # 科技蓝
  color_accent: "#00FF88"     # 荧光绿
  font_primary: "阿里巴巴普惠体"
  logo_position: "top-left"
  transition_style: "smooth_fade" # 柔和过渡
  lower_third_style: "圆角卡片-白底"
  bgm_genre: ["electronic", "ambient"]
  narration_style: "亲切自然"
  color_grading: "明亮通透"
```

#### 🔪 第二刀：叙事引擎 → 同一台机器能讲8个故事

```yaml
# config/narrative_angles.yaml — 叙事角度库
angles:
  pain_point:
    name: "痛点式"
    hook: "绕线效率提不上去？问题出在这里"
    structure: [pain_hook, problem, solution_intro, feature_showcase, result, cta]
    tone: "问题导向"
    best_for: "抖音获客引流"
    
  tech_hardcore:
    name: "技术硬核式"  
    hook: "0.02mm的精度，是怎么做到的"
    structure: [precision_hook, process, patent, test, spec_display, cta]
    tone: "技术自信"
    best_for: "行业影响力、展会展播"
    
  case_study:
    name: "客户证言式"
    hook: "XX电机厂用了三个月后告诉我们..."
    structure: [customer_context, pain_recall, solution, usage_scene, result_data, cta]
    tone: "真实可信"
    best_for: "信任背书、B2B询盘转化"
    
  production_line:
    name: "产线直击式"
    hook: "今天带你看看一台绕线机是怎么造出来的"
    structure: [factory_intro, material_flow, machine_action, qc_moment, finished_product, cta]
    tone: "真实感、沉浸感"
    best_for: "工厂实力展示"
    
  comparison:
    name: "参数对比式"
    hook: "传统绕线机 vs 隆江绕线机，差在哪"
    structure: [comparison_hook, old_way, new_way, spec_contrast, efficiency_gain, cta]
    tone: "数据碾压"
    best_for: "说服采购决策者"
    
  founder_voice:
    name: "创始人视角"
    hook: "我做绕线机20年，说几句实话"
    structure: [philosophy, industry_insight, design_principle, machine_showcase, promise, cta]
    tone: "行业老炮"
    best_for: "品牌IP建设、创始人账号"
    
  slow_cinematic:
    name: "慢工细活式"
    hook: ""  # 无旁白开场
    structure: [visual_hook, slow_motion, detail_shot, wide_shot, brand_card]
    tone: "氛围感"
    best_for: "高端品牌形象、官网首页视频"
    features: {no_narration: true, bgm_forward: true, subtitle_only: true}
    
  fast_tiktok:
    name: "抖音快节奏爆款式"
    hook: "这绕线速度，一分钟60个线圈"
    structure: [claim_hook, proof_footage, spec_bullet, result, cta]
    tone: "直给、冲击力"
    best_for: "抖音信息流投放"
    features: {speed_up: 1.2, big_text_overlay: true, duration: "15-25s"}

# 智能选择逻辑
selection_logic:
  priority:
    - "素材分析结果中高分镜头类型 → 推荐匹配角度"
    - "品牌预设偏好（taizhou_longjiang.json 已配）"
    - "发布平台 → 角度适配（抖音=快节奏，视频号=稳重型）"
    - "随机变量（防同质化最后一道防线）"
```

#### 🔪 第三刀：素材驱动变异 → AI主动制造差异化

这是最关键的一刀——**不是人选模板，是AI看过素材后主动决策**：

```
素材上传后，AI分析引擎输出：

  素材报告 {
    全景镜头: 1段, 清晰度0.78
    运行特写: 2段, 清晰度[0.92★, 0.85]
    屏幕/铭牌: 1段, OCR可提取参数
    工人操作: 1段, 清晰度0.71
    车间环境: 1段, 自然光线
    缺失镜头: [成品线圈特写, 多角度运行]
  }

→ 运行特写清晰度0.92（高分）→ 自动推荐「技术硬核式」
→ 屏幕OCR成功 → 自动提取参数填充字幕
→ 有工人操作 → 也可选「产线直击式」
→ 无成品特写 → 提示补拍，但不阻止生成
```

---

### 变异因子：1400+种组合

```yaml
variation_factors:
  narrative_angle:   8种   # 叙事角度
  bgm_tracks:       10首   # BGM库（同genre内随机）
  narration_speed:   3档   # 0.9x / 1.0x / 1.1x
  color_presets:     5套   # 品牌调色方案
  subtitle_styles:   4种   # 字幕样式
  transition_rhythm: 3种   # 快切/匀速/慢镜主导

  # 理论组合数：8 × 10 × 3 × 5 × 4 × 3 = 14,400
  
  prevention_rule:
    - "同一客户连续两次生成 → 强制切换至少3个因子"
    - "同一行业内客户 → 叙事角度分流，确保不撞车"
    - "新客户首次生成 → 随机角度，收集偏好反馈"
```

---

### 差异化对比：vs 剪映"一键成片"

| 剪映怎么做 | 我们怎么做 |
|-----------|----------|
| 输入文字→匹配素材库（别人的画面） | 输入**客户自己的素材**→分析亮点 |
| 模板固定、换文本不换骨架 | 模板是骨架，但叙事角度/BGM/色调/节奏全部可变 |
| 5个同行业客户用同一个模板→5条雷同视频 | 5个客户→素材不同+Brand DNA不同+角度不同=5条**完全不同**的视频 |
| 出片快，但一看就是"模板做的" | 出片也快，但**像定制** |

---

### 落地检查清单

每个新视频类型上线前，必须通过反同质化验收：

```
□ brand_dna 参数是否全部生效（颜色/字体/Logo/水印）
□ 叙事角度是否从素材分析结果驱动（非固定写死）
□ 同一素材换一个角度能否生成不同的视频
□ BGM/语速/色调是否从配置池智能选择（非固定值）
□ 连续生成2条 → 是否自动切换了至少3个变异因子
□ 不同品牌的同类型视频 → 视觉上是否明显不同
```





---

## 可视化拍摄向导（品类专属 + AI参考图生成）

> 核心洞察："不会拍"不是用户的问题，是产品做得不够好。

### 设计目标

每个行业/设备有专属的拍摄指南，配上AI生成的参考示意图，用户看图照着拍。不是一张通用纸，是「品类级可视化向导」。

### 用户路径

```
打开 Web UI
  |
  v
Step 1: 选行业
  [自动化设备] [数控机床] [注塑机]
  [冲压设备] [包装机械] [激光设备]
  [工厂产线] [实体门店] ...
  |
  v
Step 2: 选细分品类
  自动化设备 ->
  [无刷电机绕线机] [变压器绕线机]
  [电感绕线机] [飞叉绕线机]
  |
  v
Step 3: 拍摄向导（品类专属镜头组）
  镜头 1/6：绕线机全景
  [AI生成的参考示意图]
  "退后3米，让整台机器在画面中央"
  [参考图变体] [上传素材]
  < 上一镜    下一镜 >
```

### 不同品类 = 不同的专属镜头组

```
绕线机专属镜头组              数控机床专属镜头组
1 机器全景                    1 机床全身+防护门
2 绕线头飞叉特写              2 刀具切削特写
3 张力控制系统                3 主轴旋转近景
4 控制屏参数                 4 刀库换刀过程
5 成品线圈                   5 加工件表面质量
6 车间环境                   6 控制面板+程序
                             7 排屑/冷却系统
注塑机专属镜头组              8 车间环境
1 注塑机全景
2 模具开合特写
3 产品脱模瞬间
4 机械手取料
5 料筒/温控界面
6 成品堆叠展示
7 车间环境
```

### AI参考图生成：ComfyUI即时出图

用户选到具体镜头 -> 系统用预设prompt调ComfyUI -> 3秒出参考图：

用户选"无刷电机绕线机" -> "镜头2：绕线头特写"

ComfyUI prompt:
  "工业摄影风格，一台无刷电机绕线机的绕线头特写，
   飞叉在高速旋转，铜线精准排列在定子上，
   画面清晰对焦在绕线头上，浅景深背景虚化，
   背景是干净整洁的车间，科技感灯光照明，
   工业设备宣传片截图质感，1080x1920竖屏构图，
   真实照片风格，金属表面反光细节"

-> 3秒出图 -> 展示在向导页面上
-> 老板一看就懂："哦，要这样拍"
-> 拿手机照着拍 -> 素材质量直接拉满

### 参考图多角度变体（天然防同质化）

每个镜头生成不止一张参考图：

镜头2：绕线头特写
  正面平拍   |   45度斜拍   |   俯拍视角
  飞叉居中   |   展示张力器  |   展示铜线
  Reference  |   Reference  |   Reference
      -> 不同客户选不同角度 -> 天然异构

### 品类配置YAML（不写死代码）

#### config/categories/winding_machine.yaml

```yaml
category:
  name: "绕线机"
  icon: "winding_icon.png"
  description: "电机绕线设备，适合自动化绕线机厂家"
  
  sub_types:
    - id: "brushless_motor"
      name: "无刷电机绕线机"
    - id: "transformer"
      name: "变压器绕线机"
    - id: "flyer"
      name: "飞叉绕线机"
    - id: "inductor"
      name: "电感绕线机"
  
  shots:
    - id: "machine_full"
      name: "绕线机全景"
      description: "退后2-3米，整台机器居中，展示完整结构"
      reference_prompt: |
        工业摄影，绕线机全身照，机器居中，
        干净车间背景，正面平拍，竖屏1080x1920
      variants: ["正面平拍", "45度角", "略俯拍"]
      required: true
      min_duration: 5
      max_duration: 8
      
    - id: "winding_head"
      name: "绕线头飞叉特写"
      description: "手机靠近绕线头，对焦在飞叉上，拍到铜线排列"
      reference_prompt: |
        工业微距摄影，绕线机绕线头特写，
        飞叉高速旋转，铜线精密排列在定子上，
        浅景深，焦点在飞叉尖端，金属光泽
      variants: ["正面特写", "45度展示张力器", "俯拍铜线"]
      required: true
      min_duration: 3
      max_duration: 5
      
    - id: "tension_system"
      name: "张力控制系统"
      description: "拍摄张力器+线轴，展示线径控制精度"
      reference_prompt: |
        工业摄影，绕线机张力控制系统特写，
        多个线轴整齐排列，张力器细节清晰，
        线径参数标签可见，工业精密感
      variants: ["全组张力器", "单个张力器细节"]
      required: true
      min_duration: 3
      max_duration: 5
      
    - id: "control_panel"
      name: "控制屏参数"
      description: "正对触摸屏拍，保持2秒不动，展示关键参数"
      reference_prompt: |
        工业摄影，绕线机触摸屏控制界面特写，
        屏幕显示绕线参数（转速/线径/匝数/张力），
        正对屏幕无反光，操作界面现代感
      variants: ["参数主界面", "运行状态界面"]
      required: true
      min_duration: 2
      max_duration: 4
      
    - id: "finished_coil"
      name: "成品线圈"
      description: "展示绕好的线圈成品，展示工艺质量"
      reference_prompt: |
        工业产品摄影，绕线机完成的线圈成品特写，
        铜线排列整齐紧密，表面光亮，
        展示绕线精度和工艺水准，专业打光
      variants: ["单线圈特写", "多线圈排列"]
      required: true
      min_duration: 3
      max_duration: 5
      
    - id: "workshop"
      name: "车间环境"
      description: "从左到右慢扫车间全景，展示生产规模"
      reference_prompt: |
        工业摄影，自动化绕线设备车间全景，
        多台绕线机整齐排列，工人有序操作，
        干净整洁的现代工厂，自然光+车间顶灯
      variants: ["车间全景", "产线近景"]
      required: false
      min_duration: 8
      max_duration: 12
```

#### config/categories/cnc_machine.yaml

```yaml
category:
  name: "数控机床"
  icon: "cnc_icon.png"
  description: "CNC加工中心，适合数控机床厂家和加工厂"
  
  shots:
    - id: "full_body"
      name: "机床全身+防护门"
      description: "退后到能拍全整台机床，防护门关闭状态"
      reference_prompt: |
        工业摄影，数控机床全身照，防护门关闭，
        干净车间背景，正面平拍，竖屏构图
      required: true
      min_duration: 5
      
    - id: "cutting_tool"
      name: "刀具切削特写"
      description: "靠近拍摄刀具正在切削金属工件的画面"
      reference_prompt: |
        工业微距摄影，数控机床刀具切削金属工件，
        切屑飞出瞬间，对焦刀尖和工件接触点，
        金属光泽，切削液飞溅，景深效果
      required: true
      min_duration: 4
      
    - id: "spindle"
      name: "主轴旋转"
      description: "拍摄主轴高速旋转的近景，展现转速"
      reference_prompt: |
        工业摄影，数控机床主轴旋转特写，
        轻微动感模糊展现高转速，金属质感
      required: false
      min_duration: 4
      
    - id: "tool_changer"
      name: "刀库换刀"
      description: "拍摄自动换刀过程，刀臂动作的瞬间"
      reference_prompt: |
        工业摄影，数控机床自动换刀系统，
        刀臂抓取刀具瞬间，机械结构特写
      required: false
      min_duration: 4
      
    - id: "finished_part"
      name: "加工件表面质量"
      description: "拍摄加工完成的工件，展示精度和表面光洁度"
      reference_prompt: |
        工业产品摄影，数控机床加工完成的金属零件特写，
        表面光洁度高，展示精密加工水准
      required: true
      min_duration: 3
      
    - id: "control_program"
      name: "控制面板+G代码"
      description: "正对控制面板屏幕，展示自动化程序"
      reference_prompt: |
        工业摄影，数控机床控制面板特写，
        屏幕显示加工程序或参数界面，无反光
      required: false
      min_duration: 3
```

### ComfyUI 集成方案

```
# services/reference_image_generator.py
async def generate_reference(category_id, shot_id, variant=0):
    """
    调用ComfyUI生成拍摄参考图
    
    1. 从 config/categories/{category_id}.yaml 读 reference_prompt
    2. 根据 variant 选择角度变体
    3. 通过 ComfyUI API (127.0.0.1:8188) 生成图片
    4. 返回图片URL或本地路径
    """
    config = load_category_config(category_id)
    shot = config.shots[shot_id]
    
    prompt = build_variant_prompt(
        shot.reference_prompt, 
        shot.variants[variant]
    )
    
    result = await comfyui.txt2img(
        prompt=prompt,
        negative="blurry, distorted, low quality",
        width=1080, 
        height=1920,
        steps=20,
    )
    
    return result.image_url
```

### 产品完整用户流程

```
Web UI 主流程：

  [创建新视频]
      |
      +--> 选行业品类
      |     +-- 绕线机 -> 无刷电机绕线机
      |
      +--> 拍摄向导（品类专属）
      |     +-- 镜头1: 绕线机全景 [AI参考图x3] -> 上传
      |     +-- 镜头2: 绕线头特写 [AI参考图x3] -> 上传
      |     +-- 镜头3: 张力系统   [AI参考图x3] -> 上传
      |     +-- 镜头4: 控制屏参数 [AI参考图x3] -> 上传
      |     +-- 镜头5: 成品线圈   [AI参考图x3] -> 上传
      |     +-- 镜头6: 车间环境   [AI参考图x3] -> 上传
      |          |
      |     AI自动质量检查 -> 提示哪些镜头需重拍
      |
      +--> 品牌信息
      |     +-- 选已有品牌DNA 或 新建
      |     +-- 填写：公司名/Logo/配色偏好/口播风格
      |
      +--> [一键生成视频]
      |     +-- AI分析素材 -> 推荐叙事角度
      |     +-- 生成脚本+分镜
      |     +-- TTS配音+字幕
      |     +-- BGM匹配
      |     +-- 渲染输出
      |
      +--> 预览
            +-- 满意 -> 下载 / 发布
            +-- 不满意 -> 换角度再生成一条
            +-- 微调 -> 导出剪映草稿
```

### 落地优先级

| 阶段 | 内容 | 理由 |
|------|------|------|
| **P0（本周）** | 绕线机品类YAML配置文件 | 隆江自己先用起来 |
| **P1（验证后）** | Web UI 拍摄向导 + AI参考图生成 | 有了第一条视频后开发界面 |
| **P2** | 拓展3-5个品类（数控机床/注塑机/冲压） | 验证跨品类复用 |
| **P3** | 用户自定义品类 + 自定义镜头组 | 平台化/SaaS化 |

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

**已实现**：SharpnessDetector, CompositionDetector, StabilityDetector, ColorDetector, FaceDetector, HandDetector, TextureDetector, TextDetector
**待实现**：SubjectDetector, SceneClassifier, 视频帧提取管线, 跨检测器评分归一化标准

---

## 开发路线图

### Phase 1：核心引擎 — 素材分析 ✅（基本完成）
- [x] AssetAnalyzer + 可插拔检测器框架
- [x] FaceDetector (面部不对称/眼睛/嘴巴)
- [x] HandDetector (手指粘连/比例/关节)
- [x] TextureDetector (纹理塑料感/拼接痕)
- [x] TextDetector (OCR乱码识别)
- [x] SharpnessDetector (Laplacian variance 清晰度评分)
- [x] CompositionDetector (显著区域+三分法构图分析)
- [x] StabilityDetector (光流法抖动检测)
- [x] ColorDetector (直方图+色偏/过曝/欠曝)
- [ ] SubjectDetector (产品/人物/设备主体识别)
- [ ] 视频帧提取+逐帧分析管线 (底层已有逐帧读取，缺专用管线)
- [ ] 跨检测器评分归一化标准

### Phase 2：方案生成 — 脚本+配音+发布策略
- [x] ScriptGenerator (script_generator.py 31KB + script_engine.py 23KB, DeepSeek驱动)
- [x] TTSBuilder (tts_builder.py + tts_providers.py, Edge TTS为主)
- [x] LLM Provider 层 (llm_providers.py, DeepSeek→Qwen→Ollama fallback链)
- [x] BGM系统 (bgm_mixer.py + bgm_library 8首曲库)
- [ ] BrandDNA Manager (brand_loader.py 有基础加载，缺完整管理界面)
- [ ] TitleGenerator (多平台标题+标签+封面方案)
- [ ] CoverDesigner (封面图自动生成)
- [ ] 内容质量审核器 (quality_checker.py 有基础实现)

### Phase 3：视频合成 — Timeline→MP4
- [x] CompositionBuilder (composition_builder.py, HTML+GSAP→Chromium→MP4)
- [x] SubtitleEngine (subtitle_engine.py, SRT生成+叠加)
- [x] BGM混音 (bgm_mixer.py, 多轨混音+人声/BGM平衡)
- [x] ChromiumRenderer (chromium_renderer.py, Playwright headless渲染)
- [x] 剪映导出 (jianying_exporter.py 33KB, 支持导出到剪映编辑)
- [x] 素材管理 (asset_pipeline.py + storyboard_mapper.py)
- [x] SFX音效库 (sfx_library.py)
- [x] 电商组件 (components_ecommerce.py, 产品展示专用组件)
- [ ] TimelineEngine (参数化时间轴 — 目前直接嵌入composition_builder)
- [ ] 5套独立视频风格HTML模板 (ai_flaw_detect 有内联样式，其他类型待模板化)
- [ ] Brand 水印/Logo叠加自动化
- [ ] AvatarIntegrator (数字人集成)

### Phase 4：发布+质量 — 企业级量产（均未开发）
- [ ] PlatformAdapter (单视频→四平台版本)
- [ ] PublishStrategy 生成器
- [ ] PaidPromotion 方案生成
- [ ] QualityGate 自动审核+AutoFix
- [ ] BatchScheduler 参数化批量生产
- [ ] publishing/ 目录不存在
- [ ] quality/ 目录不存在
- [ ] scheduler/ 目录不存在

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

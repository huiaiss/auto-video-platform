# 帧导管线 — 实测质量审计报告

> 日期: 2026-05-24
> 方法: 跑 benchmark_pipeline.py，逐阶段测量时间、检查输出、定位根因

---

## 一、实测数据

### 管线耗时

| 阶段 | 耗时 | 占比 |
|------|------|------|
| 数据加载 | <0.01s | 0% |
| 产品分析(读缓存) | <0.01s | 0% |
| 脚本生成 | 0.07s | 78% |
| 素材管线 | 0.01s | 11% |
| 故事板 | <0.01s | 0% |
| HTML生成 | <0.01s | 0% |
| 验证 | <0.01s | 0% |
| **总耗时** | **0.09s** | — |

**关键发现**: 总耗时0.09秒意味着管线只做了"组装已有数据→HTML"这一步。以下环节都没有实际执行:
- TTS语音合成 → 没跑
- AI场景图生成 → 没跑  
- Chromium渲染MP4 → 没跑
- 商品套图合成(C1) → 没跑
- 真实的产品分析API调用 → 没跑(用的缓存)

### 脚本输出

| 指标 | 值 |
|------|---|
| Beats | 7 |
| 总时长 | 32.5s |
| 标题 | "155穿出170既视感！这双厚…" |
| Beat情绪分布 | hook→curiosity→trust→desire→trust→desire→action |

### HTML输出

| 指标 | 值 |
|------|---|
| 文件大小 | 25.5KB |
| 行数 | 838行 |
| GSAP | ✅ (加载自jsdelivr) |
| 品牌色 | ❌ 使用AI照妖镜默认色 |
| 组件渲染 | 5/6 (缺before-after) |
| 基础验证 | 9/12通过 |

---

## 二、定位到的三个根因

### Bug 1: 品牌色断链 [P0]

**现象**: HTML中 `--brand-primary: #00e676` (绿色), `--brand-accent: #ff1744` (红色)
**期望**: `--brand-primary: #F5F0E8` (米白), `--brand-accent: #B07D5B` (暖棕)

**根因链**:
```
creative_brief.color_palette  ← 颜色在这里
    │
    ✗ 断链！_build_ref_analysis() 接收的是 plan，不是 full data
    │
plan.shooting_template_card.color_palette  ← NOT FOUND
plan.color_palette                         ← NOT FOUND
    │
_build_ref_analysis() → brand_style = {}  (空!)
    │
_extract_brand_style() → returns {}
    │
CompositionBuilder → primary = "#00e676" (硬编码默认值)
```

**修复位置**: `pipeline_bridge.py:_build_ref_analysis()`
- 需要接收 `creative_brief` 参数，从 `creative_brief.color_palette` 提取颜色
- 或将 `plan` 传入前先注入 `color_palette`

### Bug 2: 素材管线全空匹配 [P0]

**现象**: 8个beat全部 NONE，0/8本地素材命中
**期望**: 11张场景图应该匹配到7个beat

**根因链**:
```
Beat.visual = "主角坐在窗边椅子上，翘起二郎腿…"
Scene文件名 = "scene_01_街角咖啡店_31fd45.png"
                │
_match_local(): visual关键词 ∩ 文件名关键词 = ∅
                │
score = 0 < 3 (阈值) → 不匹配
```

**修复方向**: 
- 当前是关键词重叠匹配，beat的visual是长句描述，文件名是场景标签，词汇完全不重叠
- 方案A: 改用embedding语义匹配 (CLIP text encoder)
- 方案B: 在creative brief阶段就把场景名注入beat visual
- 方案C: 直接按索引映射 (beat1→scene1, beat2→scene2...)

### Bug 3: before-after组件永远不触发 [P1]

**现象**: 6个电商组件只有5个被使用
**根因**: `_pick_component_ecommerce()` 匹配 `before-after` 的条件是 `animation == "slide"`，但所有beat的animation字段都未设置，没有beat触发slide动画

实际上Shot1的visual就是"左右分屏对比"，是典型的before-after场景，但映射逻辑没读到visual字段

---

## 三、质量评分(数据驱动)

| 维度 | 分数 | 依据 |
|------|------|------|
| 脚本质量 | 7/10 | 7beat结构完整，情绪弧线合理，但beat视觉描述和场景图文件名是两套词汇 |
| 素材匹配 | 0/10 | 0/8命中，管线完全没发挥作用 |
| 品牌一致性 | 2/10 | 品牌色断链，HTML用AI照妖镜配色 |
| 组件覆盖 | 7/10 | 5/6组件使用，before-after未触发 |
| HTML完整度 | 6/10 | 结构完整但品牌色错、素材空 |
| C1出图 | 0/10 | 完全未整合 |
| C2出片 | 4/10 | HTML生成OK，但MP4实际渲染从未验证 |
| 竞品感知 | 0/10 | 完全没有 |
| **综合** | **3.3/10** | — |

---

## 四、和之前"纸上架构"的差距

| 我声称的 | 实测的 |
|---------|--------|
| "创意大脑75%完成" | 产品分析用缓存数据，从未实时跑过API |
| "素材管线已通" | 0/8命中，关键词匹配机制完全失效 |
| "品牌色自动注入" | 断链，一直用绿色默认值 |
| "6个电商组件全覆盖" | 5/6，before-after永远不触发 |
| "出片管线70%完成" | HTML组装OK，MP4从未渲染 |
| "出图管线待整合" | 代码散落两个项目，0%不是5% |

---

## 五、修正后的真实进度

```
A. 产品分析 ✅ (代码有，但缺API实时测试)
   └─ 品牌色注入 ❌ (数据断链)
   
B. 脚本生成 ✅
   └─ 素材匹配 ❌ (机制失效)
   └─ 场景图生成 ❌ (只有程序化纹理)
   └─ TTS ❓ (从未在本机跑过)
   
C1. 商品出图 ❌ (代码在visual-hub，未迁入帧导)
   
C2. HTML组装 ⚠️ (结构OK，品牌色错，素材空)
   └─ MP4渲染 ❌ (从未实际跑过Chromium录制)
```

---

## 六、怎么解

不是继续画架构。是:

1. **修品牌色** — 改 `_build_ref_analysis()` 接收 `creative_brief` 参数 (10分钟)
2. **修素材匹配** — 把场景名注入beat的visual字段，或改用索引映射 (30分钟)
3. **跑完整MP4渲染** — 实际跑一次Chromium录制+FFmpeg混流 (1小时)
4. **迁C1出图代码** — image_processor + platform_adapter 从visual-hub迁入 (2小时)
5. **跑一次真正的端到端** — 从产品图到ZIP交付 (2小时)

总共1天的工作量，全部是修断链和补缺失的执行环节。不需要新的架构设计。

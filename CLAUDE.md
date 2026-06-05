# Auto Video Platform — 制造业AI询盘工厂

> 定位修正：2026-06-04 | 当前状态：2026-06-05
> **🔴 审计：全站 52/100 → 7个P0待修 → 报告 docs/全盘审计-2026-06-05.md**
> 
> **不是视频工厂，是询盘工厂。出片子是手段，收到询盘是目的。**

## 🔴 待修复任务（2026-06-05 Hermes 审计后派发）

### 本周必修（P0）
| # | 任务 | 工作量 | 操作指南 |
|---|------|--------|----------|
| 1 | **产品页加实拍图** | 3h | E:\隆江产品图 车间图 LOGO\ 有 4 张设备图，匹配到对应产品页。其余用豆包根据设备名生成。 |
| 2 | **英文产品页 SEO 翻译** | 1h | 44 个 en/products/*.html 的 title/description/keywords 全是中文，批量翻译成英文 |
| 3 | **修复 robots.txt AI 爬虫冲突** | 5min | 当前 Cloudflare Managed robots.txt 禁了 GPTBot/ClaudeBot/Google-Extended，但下面又 Allow: /。矛盾。修改 deploy/robots.txt 覆盖 Cloudflare 自动配置 |
| 4 | **Sitemap URL 统一加 www** | 10min | 当前 sitemap 90 个 URL 全是 longjiang-ai.com（无 www），但实际域名是 www.longjiang-ai.com。全局替换 |
| 5 | **品牌色统一** | 20min | 首页用 #0066cc，其余 86 页用 #0057b8。统一为 #0066cc |

### 两周内（P1）
| # | 任务 | 说明 |
|---|------|------|
| 6 | 产品 meta description 去模板化 | 74 个产品页只用了 2-4 种模板描述 |
| 7 | 全站加 OG 标签 | 除首页外都没 OG，分享到微信/Facebook 显示空白卡片 |
| 8 | 图片转 WebP + 压缩 | 9 张图 2.2MB 全 JPG/PNG |
| 9 | 加 favicon | 浏览器标签页空白图标 |

## 当前进度

| 步骤 | 状态 | 说明 |
|------|------|------|
| Stage 1-3 管线 | ✅ | 跑通，HDR→SDR映射、Ducking混音、HyperFrames动画字幕 |
| 3个P0修复 | ✅ | Vision prompt、文案截断、start_s时间戳 |
| 四平台发布层 | ✅ | 抖音/快手/小红书/视频号差异化策略（publish_plan.json） |
| GEO结构化数据 | ✅ | 39份PPT→products-geo.json（2065行，5类设备） |
| 落地页模板引擎 | ✅ | 37个设备专属页面，纯静态HTML+JSON-LD |
| Seedance图生视频 | 📋 | 之后再做 |

## 关键文档

| 文档 | 内容 |
|------|------|
| docs/闭环管道-v1.md | 发布层+GEO+落地页完整方案 |
| docs/竞品-追马网架构.md | 追马网全架构 + auto对标 |
| docs/竞品-霸首网架构.md | 霸首网全架构 + auto差异化 |
| docs/longjiang-ai-architecture.md | ✅ 域名整合架构设计（对标霸首网漏斗模型） |
| docs/deployment-cloudflare.md | ✅ Cloudflare Pages 部署方案 + DNS配置 |
| configs/brands/products-geo.json | 39个设备GEO数据 |
| configs/brands/taizhou_longjiang.json | 品牌配置（含完整产品参数） |
| configs/ppt_all_raw.json | 39份PPT原始文本 |
| output/landing/ | 37个设备落地页（已统一改造） |
| index.html | ✅ 首页（Hero+分类+优势+CTA） |
| robots.txt | ✅ AI爬虫友好配置 |
| sitemap.xml | ✅ 45 URLs 站点地图 |
| builders/patch_landing.py | ✅ 落地页批量改造工具 |
| builders/build_sitemap.py | ✅ sitemap自动生成工具 |

---

## 一、总览

```
┌─────────────────────────────────────────────────────────────┐
│                      用户扔素材                              │
│               D:/隆江视频素材/*.MP4 (5段)                     │
└────────────────────────┬────────────────────────────────────┘
                         ▼
╔═══════════════════════════════════════════════════════════════╗
║                    Stage 1 — 视频粗剪                          ║
║  素材→场景检测→片段评分→TopN选取→HDR映射→拼接→静音输出         ║
║  输出: stage1/roughcut.mp4                                     ║
╠═══════════════════════════════════════════════════════════════╣
║                 🔍 粗剪审计 (audit_roughcut.py)                ║
║  黑帧/冻结/时长/过曝/场景切换 → PASS 或 FAIL+修复建议           ║
╠═══════════════════════════════════════════════════════════════╣
║                    Stage 2 — 脚本生成                          ║
║  抽帧→视觉模型分析→LLM生成分镜脚本(storyboard.json)            ║
║  输出: stage2/script.json                                      ║
╠═══════════════════════════════════════════════════════════════╣
║                 🔍 脚本审计 (audit_script.py)                  ║
║  品牌/字数/emotion/尾帧/时戳对齐 → PASS 或 FAIL+修复建议        ║
╠═══════════════════════════════════════════════════════════════╣
║                    Stage 3 — 后期整合                          ║
║  roughcut + script → drawtext叠加 → BGM混音 → 尾帧 → 编码     ║
║  输出: stage3/final.mp4                                        ║
╠═══════════════════════════════════════════════════════════════╣
║                 🔍 整合审计 (audit_compose.py)                 ║
║  编码/大小/花屏/文字可读/品牌尾帧 → PASS 或 FAIL+修复建议       ║
╚═══════════════════════════════════════════════════════════════╝
                         ▼
                  成品宣传片.mp4
```

**门控规则**：每阶段产出 → 对应审计脚本 → 5/5通过才放行 → 任一不通过退回重做（最多3次）→ 超3次暂停等用户决策。

---

## 二、Stage 1 — 视频粗剪

### 输入
- `D:/隆江视频素材/IMG_0346.MP4` (21.8s)
- `D:/隆江视频素材/IMG_0347.MP4` (173.8s)
- `D:/隆江视频素材/IMG_0348.MP4` (30.5s)
- `D:/隆江视频素材/IMG_0349.MP4` (6.6s)
- `D:/隆江视频素材/431ae8d679b14bab855dc72e283e0944.MP4`

### 处理流程

```
Step 1.1  素材扫描
  → 扫描目录，收集所有MP4
  → ffprobe提取: 时长、分辨率、编码、色彩空间

Step 1.2  HDR→SDR 色调映射（关键！）
  → 检测 yuv420p10le + arib-std-b67（iPhone HLG）
  → 应用滤镜链:
    zscale=t=linear:npl=100,format=gbrpf32le,
    zscale=p=bt709,tonemap=hable:desat=2,
    zscale=t=bt709:m=bt709:r=tv,format=yuv420p

Step 1.3  场景检测 + 片段切分
  → ffmpeg select='gt(scene,0.3)' 检测切换点
  → 按切换点切分为候选片段(每个2-10秒)
  → 对每个片段评分:
    - 清晰度 (Laplacian方差)
    - 运动量 (光流均值，避免静止画面)
    - 亮度适中性 (histogram分析，排除过曝/死黑)

Step 1.4  智能选取 Top N
  → 目标：选出覆盖绕线机不同工序的N个最佳片段
  → 工序多样性权重: 绕线/张力/操作/成品 各至少1个
  → 素材源分散: 至少使用3个不同素材源
  → 总时长控制在30-60秒

Step 1.5  ffmpeg拼接
  → concat demuxer拼接选定片段
  → 编码: libx264 Main Profile, yuv420p, bt709
  → 静音输出（BGM在Stage 3加入）
  → 输出: output/stage1/roughcut.mp4
```

### 输出
- `D:/auto-video-platform/output/stage1/roughcut.mp4`
- 格式: h264/Main/yuv420p/bt709, 横版1920×1080, 30-60秒

### 🔍 粗剪审计 — `auditors/audit_roughcut.py`

| # | 检查项 | 工具 | 通过条件 |
|---|--------|------|---------|
| 1 | 无黑帧段落 | `ffmpeg blackdetect=d=0.5:pix_th=0.1` | stderr无"black_start" |
| 2 | 无>2秒冻结帧 | `ffmpeg freezedetect` | 无freeze_duration>2s |
| 3 | 时长30-60秒 | `ffprobe duration` | 30 ≤ dur ≤ 60 |
| 4 | 无过曝/死黑 | 抽4帧体积检测 | 每帧>500B |
| 5 | 有场景切换 | `ffmpeg select='gt(scene,0.3)'` | 切换≥2次 |

**调用**: `python auditors/audit_roughcut.py output/stage1/roughcut.mp4`
**结果**: exit 0=PASS, exit 1=FAIL（同时写AUDIT_PASS.txt或AUDIT_FAIL.txt）

---

## 三、Stage 2 — 脚本生成

### 输入
- `output/stage1/roughcut.mp4` — Stage 1 产出
- `taizhou_longjiang.json` — 品牌数据（公司名/slogan/电话/地址/产品参数）

### 处理流程

```
Step 2.1  关键帧提取
  → 按场景切换点 + 均匀间隔抽10-15帧
  → 每帧附时间戳

Step 2.2  视觉分析
  → 对每帧调用视觉模型（DeepSeek/Qwen vision）
  → 分析内容: 设备部位、工序阶段、画面情绪
  → 输出: [帧时间戳, 内容描述, 情绪标签]

Step 2.3  LLM 生成分镜脚本
  → 输入: 帧分析结果 + 品牌数据 + 抖音爆款脚本模板
  → LLM生成 storyboard.json:
    {
      "title": "绕线效率翻3倍？就靠它！",
      "total_duration_s": 42.6,
      "beats": [
        {
          "index": 1,
          "text": "你还在为绕线效率低头疼吗？",
          "start_s": 0, "duration_s": 3,
          "emotion": "hook",
          "visual": "特写绕线机张力器运转"
        },
        ...
      ],
      "outro": {
        "text": "台州隆江自动化 — 让绕线更智能",
        "duration_s": 6
      }
    }

  → 脚本约束（prompt中硬编码）:
    - 标题≤15字
    - 每条beat文案≤25字
    - emotion必须覆盖: hook(开头抓人), trust(建立信任), action(引导行动)
    - outro含品牌名+引导关注
    - 每个beat关联roughcut中的具体时间戳
```

### 输出
- `D:/auto-video-platform/output/stage2/script.json`

### 🔍 脚本审计 — `auditors/audit_script.py`

| # | 检查项 | 工具 | 通过条件 |
|---|--------|------|---------|
| 1 | 品牌数据准确 | JSON字段匹配 | 含"隆江"或"台州"或"自动化" |
| 2 | 文案字数规范 | len(text)统计 | 超25字条数≤3 |
| 3 | emotion分布 | JSON字段遍历 | hook/trust/action各≥1 |
| 4 | outro品牌尾帧 | outro.text检查 | 含品牌关键词 |
| 5 | 时戳对齐 | 脚本dur vs roughcut dur | 差值≤2秒 |

**调用**: `python auditors/audit_script.py output/stage2/script.json output/stage1/roughcut.mp4`
**结果**: exit 0=PASS, exit 1=FAIL

---

## 四、Stage 3 — 后期整合

### 输入
- `output/stage1/roughcut.mp4` — 纯画面流
- `output/stage2/script.json` — 分镜脚本

### 处理流程

```
Step 3.1  生成ffmpeg滤镜链
  → 遍历script.json的beats
  → 每条beat生成drawtext滤镜:
    drawtext=text='文案内容':
              fontfile=/c/Windows/Fonts/simhei.ttf:
              fontsize=size:
              fontcolor=white:
              box=1:boxcolor=black@0.5:
              boxborderw=12:
              x=(w-text_w)/2:y=h-th-80:
              enable='between(t,start_s,end_s)'

  → 字幕位置规则:
    - 主文案: 底部距边80px (y=h-th-80)
    - 副标题(产品名): 主文案上方 (y=h-th-140)
    - 字号: 主52/副46/品牌48

Step 3.2  文字叠加合成
  → ffmpeg concat输入roughcut
  → -vf 叠加所有drawtext滤镜链
  → 编码: libx264 Main, yuv420p, bt709, crf=20

Step 3.3  BGM混音（可选，Phase 2）
  → Pixabay无版权BGM
  → 音量调整为-14LUFS
  → 旁白段自动ducking

Step 3.4  品牌尾帧
  → drawtext叠加: 公司名+电话+地址+私信引导
  → 持续6秒

Step 3.5  输出编码
  → libx264 Main Profile
  → yuv420p, bt709
  → movflags +faststart（流媒体优化）
  → 输出: output/stage3/final.mp4
```

### 输出
- `D:/auto-video-platform/output/stage3/final.mp4`（<100MB，30-60秒）

### 🔍 整合审计 — `auditors/audit_compose.py`

| # | 检查项 | 工具 | 通过条件 |
|---|--------|------|---------|
| 1 | 编码兼容 | `ffprobe` v:0 stream | h264/Main/yuv420p/bt709 |
| 2 | 文件大小 | `os.path.getsize` | <100MB |
| 3 | 无花屏 | `ffmpeg signalstats` | SAT异常<5帧 |
| 4 | 抽帧有内容 | 抽4帧体积检查 | 每帧>2KB |
| 5 | 品牌尾帧 | 抽末帧体积检查 | >5KB |

**调用**: `python auditors/audit_compose.py output/stage3/final.mp4`
**结果**: exit 0=PASS, exit 1=FAIL

---

## 五、项目文件结构

```
D:/auto-video-platform/
├── CLAUDE.md                     ← 本文件（Codex每次会话必读）
├── DESIGN.md                     ← 产品愿景/竞品分析（参考用，不在CLAUDE.md）
├── taizhou_longjiang.json        ← 品牌数据
├── pipeline.py                   ← 主入口（Codex实现）
│
├── auditors/                     ← 三个车间主任（已就绪 ✅）
│   ├── audit_roughcut.py         ✅ 粗剪审计 (5项)
│   ├── audit_script.py           ✅ 脚本审计 (5项)
│   └── audit_compose.py          ✅ 整合审计 (5项)
│
├── generators/                   ← LLM+TTS 调度 (5个py文件)
├── config/
│   └── brand_loader.py           ← 品牌加载器
├── configs/
│   └── brands/taizhou_longjiang.json ← 隆江品牌数据
│
├── output/
│   ├── stage1/                   ← roughcut.mp4 + AUDIT_PASS/FAIL.txt
│   ├── stage2/                   ← script.json + AUDIT_PASS/FAIL.txt
│   └── stage3/                   ← final.mp4 + AUDIT_PASS/FAIL.txt
│
├── assets/
│   ├── bgm/corporate_tech.mp3    ← 默认BGM
│   ├── sfx/ (6个)                ← 音效
│   └── generated/ (5个)          ← ComfyUI生成资产
│
└── bgm_library/                  ← 14首BGM曲库
```

---

## 六、技术栈

| 层 | 工具 | 用途 |
|----|------|------|
| 视频合成 | ffmpeg (libx264/zscale/tonemap/drawtext) | 全部视频处理 |
| 场景检测 | ffmpeg select + scene filter | 自动切分片段 |
| 质量评分 | Python numpy+OpenCV | 清晰度/运动量/亮度评分 |
| 视觉分析 | 豆包 Seed 1.6 Vision (Ark API) | 帧内容描述 |
| 脚本生成 | Claude/DeepSeek LLM | 分镜脚本JSON |
| 音频 | ffmpeg aac/volume/loudnorm | BGM混音 |
| 字体渲染 | ffmpeg drawtext + 微软雅黑/黑体 | 品牌文字叠加 |
| HDR映射 | ffmpeg zscale + tonemap=hable | iPhone素材→SDR |
| 管道编排 | Python subprocess | 串联所有步骤 |
| 审计门控 | audit_*.py + exit code | 每阶段质量把关 |

---

## 七、素材关键参数（已实测验证 ✅）

所有素材为 **iPhone HDR**: 10-bit HLG/BT.2020 (yuv420p10le, arib-std-b67)

**直接转SDR会过曝** → 必须用色调映射:

```bash
zscale=t=linear:npl=100,format=gbrpf32le,\
zscale=p=bt709,tonemap=hable:desat=2,\
zscale=t=bt709:m=bt709:r=tv,format=yuv420p
```

**字体路径**（Windows bash环境）:
```
/c/Windows/Fonts/simhei.ttf    # 黑体
/c/Windows/Fonts/msyh.ttc      # 微软雅黑
```

**drawtext中文示例**（已验证可用）:
```bash
ffmpeg -i video.mp4 -vf \
  "drawtext=text='台州隆江自动化设备':\
   fontfile=/c/Windows/Fonts/simhei.ttf:\
   fontsize=52:fontcolor=white:\
   box=1:boxcolor=black@0.5:boxborderw=12:\
   x=(w-text_w)/2:y=h-th-80:\
   enable='between(t\\,0\\,6)'" \
  -c:v libx264 -preset medium -crf 20 \
  -pix_fmt yuv420p -profile:v main \
  -colorspace bt709 -movflags +faststart \
  output.mp4
```

**注意**: enable参数中的逗号需转义为 `\\,`；必须在bash中执行（Python subprocess有引号转义问题）。

---

## 八、环境

- OS: Windows 10 Pro
- GPU: RTX 3060 Ti 8GB
- Python: C:/Python314
- ffmpeg: 8.1.1 essentials (含libzimg/libilbc/libx264)
- Node.js: v24.15.0
- ComfyUI: http://127.0.0.1:8188
- 素材: D:/隆江视频素材/ (5段iPhone HDR MP4)

---

## 九、铁律

- Claude说"完成" → Hermes独立验证
- 每阶段产出必须通过审计才能进入下一阶段
- 重做>3次自动暂停，通知用户
- CLAUDE.md是工作手册，DESIGN.md是参考文档
- 发现问题→先更新CLAUDE.md→再汇报

---

## 十、Codex协作规则

1. **先读CLAUDE.md** — 每次会话启动必读
2. **先读shared-context.md** — 了解团队最新动态
3. **代码修改前置闸门** — 改代码前必须先web_search并填表
4. **一步一验** — 改完一步等验证通过再做下一步
5. **Pipeline调用审计**:
   ```bash
   # Stage 1
   python pipeline.py stage1 && python auditors/audit_roughcut.py output/stage1/roughcut.mp4
   # Stage 2
   python pipeline.py stage2 && python auditors/audit_script.py output/stage2/script.json output/stage1/roughcut.mp4
   # Stage 3
   python pipeline.py stage3 && python auditors/audit_compose.py output/stage3/final.mp4
   ```
   任一审计失败 → pipeline中断 → 读AUDIT_FAIL.txt → 修复 → 重跑

---

## 十一、当前状态

| 组件 | 状态 |
|------|------|
| ffmpeg合成方案 | ✅ demo_v2.mp4验证通过（27.6s实拍+文字） |
| 三个审计脚本 | ✅ 已就绪 + GBK编码已修复 |
| 审计脚本-整合 | ✅ 5/5 PASS实测 |
| Stage 2 视觉分析 | ✅ DeepSeek Vision已验证：能识别绕线机部件/工序/文案 |
| HTML→Chromium方案 | ❌ 已废弃 |
| Stage 1 pipeline.py | ⏳ 归Claude Code |
| Stage 2 pipeline.py | ⏳ 归Claude Code（视觉分析链路已验证可行） |
| Stage 3 pipeline.py | ⏳ 归Claude Code |
|| BGM集成 | ⏳ Phase 2 (从FrameCraft搬) |
|| ComfyUI特效叠加 | ⏳ Phase 2 |
|| 🌐 域名整合 `longjiang-ai.com` | 🔴 P0-新任务 (2026-06-05) |

---

## 十二、🌐 域名整合任务 — `longjiang-ai.com`

### 背景

用户选定域名 `longjiang-ai.com`（.com后缀，国内正常备案）。对标霸首网架构，域名不只是挂静态页，而是把 **视频生产 → 搜索拦截 → 落地页 → 询盘** 整条漏斗串在一个域名下。

### 对标霸首网

```
霸首网: 热点抓取→48h出片→矩阵发布→搜索拦截→落地页留资
auto:  素材扔入→Stage1-3自动出片→GEO数据→落地页→询盘
                                          ↑
                                    差个域名把最后三步串起来
```

### 目标架构

```
longjiang-ai.com
├─ /                          ← 首页（视频展示+设备导航）
├─ /products/LJ-9WD-1.html   ← 37个设备GEO落地页（已有）
├─ /videos/                   ← auto生成的视频展示页
├─ /cases/                    ← 客户案例
├─ /contact/                  ← 询盘表单 → tel:18968693691
├─ /sitemap.xml               ← AI爬虫入口（自动更新）
└─ /robots.txt                ← 允许所有AI爬虫
```

### 待 Claude 做的事

1. **域名购买**：用户自己在阿里云买 `longjiang-ai.com`（约78元首年）
2. **托管方案选型**：推荐 Cloudflare Pages（免费+对AI爬虫友好）或阿里云OSS
3. **落地页改造**：37个HTML加上统一的导航/页脚/询盘按钮
4. **首页设计**：视频轮播+设备分类导航+询盘入口
5. **视频展示页**：auto出片后自动生成视频展示页
6. **sitemap.xml**：自动生成+自动提交到百度/Google/DeepSeek/豆包
7. **AI爬虫友好标记**：JSON-LD结构化数据 + Schema.org标记
8. **DNS/备案**：阿里云备案流程（.com国内服务器必须备案）

### 进度

- [x] **域名注册** — ✅ 用户在阿里云已买 longjiang-ai.com（当前DNS未配置）
- [ ] **DNS配置** — 见下方 DNS 配置指引（阿里云DNS解析设置页面记录数为0）
- [ ] **托管部署** — 方案已就绪见 `docs/deployment-cloudflare.md`
- [x] **落地页整合(中文)** — ✅ 37个页面已统一改造（导航/页脚/浮动CTA/canonical/OG/JSON-LD更新）
- [x] **首页(中文)** — ✅ 已创建 `index.html`
- [ ] **🌐 双语B2B独立站** — 🔴 新任务 (2026-06-05) 中文/英文双版本，对标霸首网漏斗模型
- [ ] **英文版落地页** — 待生成 37个 `/en/products/*.html` + 英文首页/关于/联系
- [x] **sitemap + AI爬虫提交** — ✅ `sitemap.xml`（45 URLs）+ `robots.txt`
- [ ] **备案** — 建议走阿里云ICP备案流程（10-20工作日）

# 🌐 longjiang-ai.com 双语B2B独立站架构

> 2026-06-05 | 对标霸首网域名漏斗模型
> 中文 + 英文 双版本，覆盖国内外 B2B 采购决策全链路

---

## 一、架构总览：双语双通道漏斗

```
                    longjiang-ai.com
                   单域名 · 双语 · 全漏斗
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │  中文版   │ │  英文版   │ │AI爬虫通道│
      │  /        │ │  /en/     │ │sitemap   │
      │百度/抖音  │ │Google/Bing│ │DeepSeek等│
      └─────┬────┘ └─────┬────┘ └─────┬────┘
            │             │             │
            └─────────────┼─────────────┘
                          ▼
                   ┌────────────┐
                   │  询盘转化   │
                   │国内:电话/微信│
                   │海外:Email   │
                   └────────────┘
```

### 核心原则

| 维度 | 策略 |
|------|------|
| 域名策略 | 单域名 longjiang-ai.com，路径区分语言（/ vs /en/） |
| 语言切换 | 导航栏右上角显式切换，URL 路径变化，不依赖 JS 动态渲染 |
| 内容同步 | 同一产品，中文页展示国内参数，英文页展示国际参数 |
| SEO/GEO | 中文站→百度/DeepSeek/豆包；英文站→Google/Bing/LinkedIn |
| 品牌一致 | 同一套视觉体系（深色工业风），同一套 CTA 体系 |

---

## 二、URL 结构树（双语完整版）

```
longjiang-ai.com
│
├─ /                                    # [中文] 首页
├─ /products/                           # [中文] 产品总览
│   ├─ /products/LJ-9WD-1.html          # 37个设备落地页
│   └─ /products/...                    # 共37个
│
├─ /videos/                             # [中文] 视频展示
├─ /cases/                              # [中文] 客户案例
├─ /contact/                            # [中文] 询盘页
├─ /about/                              # [中文] 公司介绍
│
├─ /en/                                 # [英文] 首页
├─ /en/products/                        # [英文] 产品总览
│   ├─ /en/products/LJ-9WD-1.html       # 37个英文落地页
│   └─ /en/products/...
│
├─ /en/videos/                          # [英文] Videos
├─ /en/cases/                           # [英文] Cases
├─ /en/contact/                         # [英文] Inquiry
├─ /en/about/                           # [英文] About Us
│
├─ /sitemap.xml                         # 双语站点地图
├─ /robots.txt                          # AI爬虫友好
└─ /assets/                             # 静态资源
```

---

## 三、对标霸首网漏斗模型（双语版）

| 漏斗阶段 | 霸首网 | auto 中文版 | auto 英文版 |
|----------|--------|-------------|-------------|
| 流量获取 | 追抖音热点→出片→发布 | Stage1-3出片→抖音/快手 | YouTube Shorts/LinkedIn |
| 搜索拦截 | 87%长尾词SEO | GEO→DeepSeek/豆包 | Product Schema→Google/Bing |
| 信任建立 | 工厂剧场化+老板IP | 实拍素材+参数+PPT | Factory tour+Certifications |
| 转化成交 | 评论区→私信→留资 | CTA→电话/微信/表单 | CTA→Email/WhatsApp/Form |

---

## 四、导航栏设计（双语通用）

### 4.1 语言切换器逻辑

| 当前页面 | 切换按钮 | 目标 URL |
|----------|----------|----------|
| /products/LJ-9WD-1.html | 点击 EN | /en/products/LJ-9WD-1.html |
| /en/products/LJ-9WD-1.html | 点击 中 | /products/LJ-9WD-1.html |

### 4.2 中文导航

```
[●] 隆江自动化  产品 ▼  视频  案例  关于  联系  [中 | EN]
```

### 4.3 英文导航

```
[●] Longjiang Auto  Products ▼  Videos  Cases  About  Contact  [中 | EN]
```

---

## 五、hreflang 配置

每个页面 head 中必须包含：

```html
<link rel="alternate" hreflang="zh-CN" href="https://longjiang-ai.com/products/LJ-9WD-1.html">
<link rel="alternate" hreflang="en" href="https://longjiang-ai.com/en/products/LJ-9WD-1.html">
<link rel="alternate" hreflang="x-default" href="https://longjiang-ai.com/products/LJ-9WD-1.html">
```

---

## 六、B2B 内容策略

| 内容类型 | 中文站 | 英文站 |
|----------|--------|--------|
| 设备参数页 | 37个，来自PPT数据 | 翻译+国际单位 |
| 视频 | 抖音/快手风格 | YouTube/LinkedIn风格 |
| 信任元素 | 资质/案例/工龄 | CE/ISO/Patent/Factory Tour |
| 询盘方式 | 电话 18968693691 / 微信 ljzdh888 | Email inquiry@longjiang-ai.com |

---

## 七、实施路线

```
Phase 1 (今天)  架构设计完成 + 英文首页 + 37个英文落地页生成
Phase 2 (本周)  Cloudflare Pages 部署 + 阿里云 DNS 配置
Phase 3 (下周)  英文Contact/About/Cases + 询盘表单后端
```

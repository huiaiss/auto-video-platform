# longjiang-ai.com B2B 双语独立站完整架构

> 2026-06-05 | 基于 CLAUDE.md §12 域名整合任务
> 目标：一套代码，中英双语，AI爬虫友好，询盘转化

---

## 一、核心理念：一个域名，两个语言版本

```
longjiang-ai.com
├─ /                    ← 中文首页（默认）
├─ /en/                 ← English Homepage
├─ /products/           ← 37个中文产品落地页
├─ /en/products/        ← 37 English product pages
├─ /contact/            ← 中文询盘
├─ /en/contact/         ← English Inquiry
├─ /about/              ← 中文公司介绍
├─ /en/about/           ← English About Us
├─ /videos/             ← 中文视频展示
├─ /en/videos/          ← English Videos
├─ /cases/              ← 中文案例
├─ /en/cases/           ← English Cases
├─ /sitemap.xml         ← 聚合 sitemap
├─ /sitemap-zh.xml      ← 中文 sitemap（提交百度）
├─ /sitemap-en.xml      ← English sitemap（提交 Google）
└─ /robots.txt          ← AI爬虫全开放
```

### 选择子目录 `/en/` 的理由

| 方案 | SEO | 维护成本 | 推荐度 |
|------|-----|---------|-------|
| 子域名 `en.longjiang-ai.com` | 被搜索引擎视为独立站点，权重分散 | 需单独配置 DNS/SSL | ❌ |
| 子目录 `/en/` | 权重集中到主域，hreflang 明确 | 同一套代码，同一部署 | ✅ |
| 参数 `?lang=en` | URL 不友好，AI爬虫不识别 | 最简单 | ❌ |
| 双语同页 | 内容重复，SEO 惩罚风险 | 无需切换 | ❌ |

---

## 二、品牌双语映射表

| 中文 | English |
|------|---------|
| 台州隆江自动化 | Longjiang Automation |
| 台州隆江自动化设备有限公司 | Taizhou Longjiang Automation Equipment Co., Ltd. |
| 让绕线更智能 | Smarter Winding Solutions |
| 首页 | Home |
| 产品 | Products |
| 视频 | Videos |
| 案例 | Cases |
| 关于 | About Us |
| 联系 | Contact |
| 电话咨询 | Call Us |
| 微信询价 | WeChat Inquiry |
| 获取方案 | Get Solution |
| 全部产品 | All Products |
| 绕线机 | Winding Machine |
| 磁钢机 | Magnet Machine |
| 插纸机 | Paper Inserter |
| 其他设备 | Other Equipment |
| 产品中心 | Products |
| 关于我们 | About Us |
| 服务支持 | Service |
| 联系方式 | Contact Info |
| 公司介绍 | Company Profile |
| 客户案例 | Customer Cases |
| 服务承诺 | Service Commitment |
| 源头工厂 · 省级科技型企业 | Factory Direct · Provincial Tech Enterprise |
| 制造业AI询盘工厂 | AI-Powered Inquiry Engine |
| 让每一台设备被精准找到 | Helping Your Machines Get Found |
| 免费样机打样 | Free Sample Testing |
| 技术工程师 1 对 1 对接 | 1-on-1 Technical Consultation |

---

## 三、导航栏设计（双语切换）

### 3.1 桌面端导航

```
┌──────────────────────────────────────────────────────────────┐
│ [●] 隆江自动化/Longjiang Auto                               │
│                                                              │
│  首页/Home │ 产品/Products ▼ │ 视频/Videos │ 案例/Cases     │
│  关于/About │ 联系/Contact  │ [🌐 中文/English]  📞          │
├──────────────────────────────────────────────────────────────┤
│  ┌─ 绕线机/Winding Machine ─┐                                │
│  │ 磁钢机/Magnet Machine     │  ← 下拉菜单                   │
│  │ 插纸机/Paper Inserter     │                                │
│  └─ 全部/All ───────────────┘                                │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 语言切换逻辑

```javascript
// 语言切换器逻辑
// 1. 用户点击 [🌐 中文/English]
// 2. 检测当前页面路径:
//    - 如果当前在 /products/xxx.html → 跳转 /en/products/xxx.html
//    - 如果当前在 /en/products/xxx.html → 跳转 /products/xxx.html
//    - 如果当前在 / → 跳转 /en/
//    - 如果当前在 /en/ → 跳转 /
// 3. 存储偏好到 localStorage
// 4. 下次访问自动跳转
```

### 3.3 移动端导航

```
┌──────────────────┐
│ [●] 隆江  ☰ [🌐] │  ← 右上角语言切换
├──────────────────┤
│ 首页 Home        │
│ 产品 Products ▼  │
│ 视频 Videos      │
│ 案例 Cases       │
│ 关于 About       │
│ 联系 Contact     │
└──────────────────┘
```

---

## 四、37个产品落地页双语方案

### 4.1 策略：中文为主 + 英文摘要

```
每一个产品页同时包含中文和英文内容：

┌─ HTML结构 ──────────────────────────────────────────────┐
│ <html lang="zh-CN">                                      │
│ <head>                                                   │
│   <link rel="alternate" hreflang="zh-CN" href="..." />   │
│   <link rel="alternate" hreflang="en" href="..." />      │
│   <link rel="alternate" hreflang="x-default" href="..."> │
│ </head>                                                  │
│ <body>                                                   │
│   导航栏（双语标签 + 语言切换）                          │
│                                                          │
│   产品参数区域（保持中文原文）                           │
│   JSON-LD（中英双语）                                    │
│                                                          │
│   页脚（双语）                                           │
│   浮动CTA（双语）                                        │
│ </body>                                                  │
└──────────────────────────────────────────────────────────┘
```

### 4.2 英文版生成计划

由于37个产品页内容为中文，推荐分阶段实施：

| 阶段 | 内容 | 方法 |
|------|------|------|
| Phase 1 (今日) | 统一导航/页脚/CTA 双语化 | `patch_landing.py` 批量注入 |
| Phase 2 (本周) | 产品名 + 核心参数 英文版 | LLM 翻译标题和参数 |
| Phase 3 (下周) | 完整英文产品页 | LLM 逐页生成 EN 版本 |

**Phase 1 今日交付**：导航/页脚/CTA 中英双语标签，语言切换按钮，hreflang SEO 标签。

---

## 五、SEO/GEO 双语策略

### 5.1 hreflang 标签

每个页面 `<head>` 中必须包含：

```html
<link rel="alternate" hreflang="zh-CN" href="https://longjiang-ai.com/products/LJ-9WD-1.html">
<link rel="alternate" hreflang="en" href="https://longjiang-ai.com/en/products/LJ-9WD-1.html">
<link rel="alternate" hreflang="x-default" href="https://longjiang-ai.com/products/LJ-9WD-1.html">
```

### 5.2 sitemap 分离

```xml
<!-- sitemap-zh.xml: 提交百度 -->
<urlset>
  <url><loc>https://longjiang-ai.com/</loc><priority>1.0</priority></url>
  <url><loc>https://longjiang-ai.com/products/LJ-9WD-1.html</loc><priority>0.8</priority></url>
  ...
</urlset>

<!-- sitemap-en.xml: 提交 Google Search Console -->
<urlset>
  <url><loc>https://longjiang-ai.com/en/</loc><priority>1.0</priority></url>
  <url><loc>https://longjiang-ai.com/en/products/LJ-9WD-1.html</loc><priority>0.8</priority></url>
  ...
</urlset>
```

### 5.3 JSON-LD 双语

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "LJ-9WD-1 三针绕线机",
  "alternateName": "LJ-9WD-1 Three-Needle Winding Machine",
  "description": {
    "zh-CN": "首末端自动预留定长线头",
    "en": "Auto预留 lead wire at both ends"
  }
}
```

---

## 六、部署架构

```
用户访问
    │
    ▼
Cloudflare CDN (330+ 节点)
    │
    ▼
Cloudflare Pages (全球)
    │
    ├─ longjiang-ai.com/        ← 中文站点
    ├─ longjiang-ai.com/en/     ← English site
    │
    ├─ DNS: 阿里云 NS → Cloudflare NS
    │
    └─ 自动部署: GitHub → Cloudflare Pages
```

### DNS 记录（阿里云 → Cloudflare）

**方案A（推荐）：Cloudflare DNS 托管**

| 记录类型 | 名称 | 值 | TTL |
|---------|------|-----|-----|
| A | @ | 192.0.2.1（CF Pages 自动管理） | Auto |
| CNAME | www | long-jiang-ai-com.pages.dev | Auto |
| TXT | @ | v=spf1 include:_spf.mx.cloudflare.net ~all | Auto |
| NS | @ | (Cloudflare 提供的4个NS地址) | — |

**方案B（简化）：阿里云 DNS CNAME 直指**

| 记录类型 | 名称 | 值 | TTL |
|---------|------|-----|-----|
| CNAME | @ | long-jiang-ai-com.pages.dev | 600 |
| CNAME | www | long-jiang-ai-com.pages.dev | 600 |

### 成本

| 项目 | 费用 | 说明 |
|------|------|------|
| 域名 longjiang-ai.com | ¥78/首年 | ✅ 已在阿里云注册 |
| Cloudflare Pages | ¥0/月 | 免费套餐够用 |
| SSL 证书 | ¥0 | Cloudflare 自动提供 |
| **总计首年** | **¥78** | |

---

## 七、实施路线

```
Phase 1（今日）✅
├─ 架构设计文档（本文件）
├─ 37个落地页统一双语导航/页脚/CTA
├─ 首页双语改造
└─ DNS + 部署步骤输出

Phase 2（本周）
├─ 英文版首页 /en/index.html
├─ 英文版联系页 /en/contact/index.html
├─ 英文版关于页 /en/about/index.html
├─ sitemap-zh.xml + sitemap-en.xml

Phase 3（下周）
├─ 37个英文版产品落地页（LLM翻译）
├─ Google Search Console 提交
├─ DeepSeek/豆包爬虫提交
└─ ICP 备案启动
```

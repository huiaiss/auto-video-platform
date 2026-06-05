# longjiang-ai.com 部署行动手册

> 2026-06-05 | 阿里云域名已注册（DNS设置页面打开中，记录数0）

---

## 一、阿里云 DNS 需添加的记录

> **选择方案：** 先用方案B（阿里云DNS直指），上线后再升级到方案A（Cloudflare DNS托管）

### 方案B：阿里云 DNS CNAME 直指（立刻可做）

在阿里云DNS解析页面，添加 **2条记录**：

| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|--------|-----|
| **CNAME** | **@** | **long-jiang-ai-com.pages.dev** | 600 |
| **CNAME** | **www** | **long-jiang-ai-com.pages.dev** | 600 |

> ⚠️ 不要添加 A 记录。CNAME @ 用于根域名，阿里云支持CNAME拉平。

---

## 二、Cloudflare Pages 部署步骤

### 2.1 准备部署文件

项目根目录 `D:\auto-video-platform/` 已就绪：

```
longjiang-ai.com/
├── index.html              ← 中文首页
├── en/index.html           ← English homepage
├── output/landing/         ← 37个中文产品落地页
├── output/landing/en/      ← 37个英文产品落地页
├── robots.txt              ← AI爬虫友好
├── sitemap.xml             ← 90 URLs（中英文各45）
├── 404.html                ← [待创建，可选]
├── assets/                 ← [CSS/JS待整理，目前内联在HTML中]
├── contact/                ← [待创建]
├── about/                  ← [待创建]
└── cases/                  ← [待创建]
```

### 2.2 部署方式一：Wrangler CLI（推荐，5分钟）

```bash
# 1. 安装 Wrangler
npm install -g wrangler

# 2. 登录 Cloudflare
wrangler login

# 3. 部署（从项目根目录）
cd D:\auto-video-platform
wrangler pages deploy . --project-name=long-jiang-ai-com
```

### 2.3 部署方式二：Cloudflare Dashboard 手动上传

```
1. 打开 https://dash.cloudflare.com → Pages → Create a project
2. 选择 "Direct Upload"
3. 项目名称: long-jiang-ai-com
4. 上传文件:
   - 将 index.html, robots.txt, sitemap.xml 等根文件拖入
   - 点击 "Add directory" 添加 output/landing/ → 重命名为 products/
   - 创建 en/ 目录并上传 en/index.html
   - 再添加 output/landing/en/ 到 en/products/
5. 点击 "Deploy"
```

### 2.4 绑定自定义域名

```
1. Cloudflare Dashboard → Pages → long-jiang-ai-com
2. Custom domains → Set up a custom domain
3. 输入: longjiang-ai.com
4. 点击 "Continue" → "Activate domain"
5. HTTPS 自动生效（~1分钟）
```

### 2.5 验证部署

```bash
# DNS 生效后（通常1-10分钟）
curl -I https://longjiang-ai.com/
curl -I https://longjiang-ai.com/en/
curl -I https://longjiang-ai.com/products/LJ-9WD-1.html
curl -I https://longjiang-ai.com/en/products/LJ-9WD-1.html

# 验证 sitemap
curl https://longjiang-ai.com/sitemap.xml
```

---

## 三、部署后操作

### 3.1 提交 sitemap 到搜索引擎

| 搜索引擎 | 提交地址 | 操作 |
|---------|---------|------|
| **百度** | https://ziyuan.baidu.com/linksubmit/index | 添加 longjiang-ai.com，提交 sitemap.xml |
| **Google** | https://search.google.com/search-console | 添加 longjiang-ai.com，提交 sitemap.xml |
| **DeepSeek** | 通过 sitemap.xml 自动发现 | ✅ robots.txt 已配置 |
| **豆包** | 通过 sitemap.xml 自动发现 | ✅ robots.txt 已配置 |

### 3.2 验证中文/英文正常显示

```
https://longjiang-ai.com/        → 中文首页
https://longjiang-ai.com/en/     → English Home
https://longjiang-ai.com/products/LJ-9WD-1.html        → 中文产品页
https://longjiang-ai.com/en/products/LJ-9WD-1.html     → 英文产品页
```

### 3.3 后续优化

| 优先级 | 事项 | 说明 |
|--------|------|------|
| P0 | ICP备案启动 | .com国内服务器需要，10-20工作日 |
| P1 | contact/about/cases页面 | 创建完整版 |
| P1 | 英文内容翻译 | LLM翻译37个产品页描述 |
| P2 | 升级到方案A DNS | Cloudflare NS托管，获得CDN加速 |
| P2 | 创建 404.html | 自定义404页面 |

---

## 四、文件清单（部署前确认）

```
✅ index.html            — 中文首页（双语导航+语言切换+hreflang）
✅ en/index.html          — English homepage
✅ output/landing/*.html — 37个中文产品页（已注入双语导航/页脚/CTA）
✅ output/landing/en/*.html — 37个英文产品页（英文导航/页脚/CTA）
✅ robots.txt             — AI爬虫全开放
✅ sitemap.xml            — 90 URLs
❌ 404.html               — [可选，临时用Cloudflare默认]
❌ contact/index.html     — [待创建]
❌ about/index.html       — [待创建]
❌ cases/index.html       — [待创建]
```

---

## 五、成本

| 项目 | 费用 | 状态 |
|------|------|------|
| 域名 longjiang-ai.com | ¥78/年 | ✅ 已在阿里云注册 |
| Cloudflare Pages | ¥0/月 | 免费套餐 |
| SSL证书 | ¥0 | Cloudflare自动 |
| **首年合计** | **¥78** | |

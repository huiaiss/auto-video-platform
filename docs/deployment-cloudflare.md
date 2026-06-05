# longjiang-ai.com 部署方案 — Cloudflare Pages + DNS

> 2026-06-05 | 对标方案：免费、高性能、AI爬虫友好

---

## 一、选型理由

| 维度 | Cloudflare Pages | 阿里云 OSS + CDN | 自建服务器 |
|------|-----------------|-----------------|-----------|
| 月费 | 免费（5GB存储/500MB文件/500次构建/月） | 约30元/月（OSS+CDN流量） | 200元+/月 |
| HTTPS | 自动（免费SSL） | 需单独配置 | 需配置 |
| 全球CDN | ✅ 330+节点 | 仅国内 | 需自建 |
| AI爬虫友好 | ✅ 全球节点，延迟低 | ✅ | ❌ |
| 部署方式 | Git推送自动构建 | 手动上传/OssUtil | 手动部署 |
| 自定义域名 | ✅ 一键绑定 | ✅ | ✅ |
| 构建超时 | 5分钟 | N/A | N/A |

**结论：Cloudflare Pages 胜出** — 纯静态站，5分钟构建足够；免费额度完全够用；全球CDN加速对海外AI爬虫友好。

> ⚠ 注意：国内访问 Cloudflare 有时不稳定。如果国内用户是主要目标，可考虑 **Cloudflare Pages（主）+ 阿里云OSS（备）** 双部署，通过DNS分流。

---

## 二、DNS 架构

### 2.1 购买域名

在阿里云购买 `longjiang-ai.com`（约78元/首年），完成实名认证。

### 2.2 DNS 托管方案（二选一）

#### 方案A（推荐）：Cloudflare DNS

```
阿里云域名NS → 指向 Cloudflare NS → Cloudflare 管理DNS
                                                 │
                                          ┌──────┴──────┐
                                          ▼              ▼
                                    Cloudflare Pages   其他记录
```

操作步骤：
1. 在阿里云将 `longjiang-ai.com` 的 NameServer 改为 Cloudflare 的 NS
2. Cloudflare 中配置 DNS 记录：

| 类型 | 名称 | 值 | 代理 |
|------|------|-----|------|
| A | @ | 192.0.2.1（占位，实际由CF Pages自动管理） | Proxied（橙色云） |
| CNAME | www | long-jiang-ai-com.pages.dev | Proxied |
| TXT | @ | v=spf1 include:_spf.mx.cloudflare.net ~all | — |
| CNAME | _domainconnect | _domainconnect.g.domains.cloudflare.com | — |

#### 方案B：阿里云 DNS + Cloudflare Pages

```
阿里云DNS → CNAME 到 Cloudflare Pages 域名
```

| 类型 | 名称 | 值 |
|------|------|-----|
| CNAME | @ | longjiang-ai-com.pages.dev |
| CNAME | www | longjiang-ai-com.pages.dev |

> 方案A有CDN加速+隐藏源IP，推荐。

---

## 三、Cloudflare Pages 部署配置

### 3.1 创建 Pages 项目

```bash
# 1. 登录 Cloudflare Dashboard → Pages → Create a project
# 2. 选择 "Direct Upload" 或连接 Git 仓库
#    推荐连接 Git（自动部署）
#    GitHub: https://github.com/你的账号/longjiang-ai-landing
# 3. 项目名称: long-jiang-ai-com
# 4. 生产分支: main
# 5. 构建设置:
#    - Framework preset: None（纯静态）
#    - Build command: （留空）
#    - Build output directory: /（项目根目录）
#    - Root directory: （留空）
# 6. 环境变量: 无需设置
```

### 3.2 项目目录结构

```
longjiang-ai-landing/
├── index.html              ← 首页
├── 404.html                ← 自定义404
├── robots.txt              ← AI爬虫规则
├── sitemap.xml             ← 站点地图（自动生成）
├── products/               ← 37个设备落地页（直接放根）
│   ├── LJ-9WD-1.html
│   ├── 单工位飞叉外绕机.html
│   └── ...
├── videos/                 ← 视频展示页（后续生成）
│   └── index.html
├── cases/                  ← 客户案例
│   └── index.html
├── contact/                ← 询盘页面
│   └── index.html
├── about/                  ← 公司介绍
│   └── index.html
└── assets/
    ├── css/
    ├── js/
    └── img/
```

> 注：Cloudflare Pages 不支持 `.html` 扩展名自动省略。如果想实现 `/products/LJ-9WD-1` 而不是 `/products/LJ-9WD-1.html`，需要配置 `_redirects` 或 `_headers` 文件。但考虑到 SEO 和现有链接结构，保持 `.html` 扩展名更稳妥。

### 3.3 `_redirects` 文件（可选）

在项目根目录创建 `_redirects`（无扩展名）：

```
# Cloudflare Pages 重定向规则
/products/              /products/  200
/videos/                /videos/  200
/cases/                 /cases/  200
/contact/               /contact/  200
/about/                 /about/  200

# 临时重定向（如果某些产品页迁移）
/*                      /404.html  404
```

### 3.4 `_headers` 文件（可选）

```
# 安全头
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin

# 结构化数据缓存
*.json
  Cache-Control: public, max-age=3600

# 图片缓存
*.svg
  Cache-Control: public, max-age=86400
```

---

## 四、CI/CD 自动部署

### 4.1 GitHub Actions（推荐）

在项目根目录创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches: [main]
  workflow_dispatch:  # 手动触发

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          command: pages deploy . --project-name=long-jiang-ai-com
```

### 4.2 本地手动上传（备选）

```bash
# 安装 Wrangler CLI
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署
wrangler pages deploy . --project-name=long-jiang-ai-com
```

---

## 五、sitemap.xml 自动生成 + 提交

### 5.1 自动生成脚本 `builders/build_sitemap.py`

```python
#!/usr/bin/env python3
"""自动生成 sitemap.xml，包含所有产品落地页"""
import os
from datetime import datetime

DOMAIN = "longjiang-ai.com"
LANDING_DIR = "output/landing"
OUTPUT = "sitemap.xml"

pages = [
    {"loc": "/", "priority": "1.0"},
    {"loc": "/products/", "priority": "0.9"},
    {"loc": "/videos/", "priority": "0.8"},
    {"loc": "/cases/", "priority": "0.7"},
    {"loc": "/contact/", "priority": "0.9"},
    {"loc": "/about/", "priority": "0.6"},
]

# 扫描 landing 目录
for fname in sorted(os.listdir(LANDING_DIR)):
    if fname.endswith(".html"):
        name = fname.rsplit(".", 1)[0]
        pages.append({
            "loc": f"/products/{name}.html",
            "priority": "0.8"
        })

today = datetime.now().strftime("%Y-%m-%d")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for p in pages:
    xml += '  <url>\n'
    xml += f'    <loc>https://{DOMAIN}{p["loc"]}</loc>\n'
    xml += f'    <lastmod>{today}</lastmod>\n'
    xml += f'    <priority>{p["priority"]}</priority>\n'
    xml += '  </url>\n'
xml += '</urlset>\n'

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(xml)
print(f"✅ sitemap.xml generated with {len(pages)} URLs")
```

### 5.2 提交到搜索引擎

```bash
# 百度搜索资源平台
https://ziyuan.baidu.com/linksubmit/index  # 手动提交

# Google Search Console
# 自动：登录 GSC → 添加 longjiang-ai.com → 验证所有权 → 提交 sitemap

# DeepSeek 爬虫（DeepBot/1.0）
# 当前暂无公开提交入口，通过 robots.txt 和 sitemap.xml 自动发现

# 豆包爬虫
# 同样通过 sitemap.xml 自动发现
```

---

## 六、落地页迁移工作流

从当前 `output/landing/` 部署到 Cloudflare Pages 的完整流程：

```bash
# 1. 本地确认改造后的落地页
cd D:/auto-video-platform
python builders/patch_landing.py

# 2. 生成 sitemap.xml
python builders/build_sitemap.py

# 3. 复制到部署目录
mkdir -p deploy/products
copy output/landing/*.html deploy/products/
copy index.html deploy/
copy robots.txt deploy/
copy sitemap.xml deploy/

# 4. （可选）创建首页、contact、about 等缺失页面

# 5. 使用 Wrangler 部署
cd deploy
wrangler pages deploy . --project-name=long-jiang-ai-com

# 6. 绑定自定义域名
# Cloudflare Dashboard → Pages → long-jiang-ai-com → Custom domains
# 添加 longjiang-ai.com
```

---

## 七、备案说明

| 平台 | 是否需要备案 | 说明 |
|------|------------|------|
| Cloudflare Pages | 不需要 | Cloudflare 全球CDN，境外节点无需中国备案 |
| 阿里云 OSS（备选） | 需要 | 国内节点必须ICP备案 |
| 阿里云 DNS | 不需要 | 仅DNS解析无需备案 |

**建议流程**：
1. 立即用 Cloudflare Pages + 境外节点上线（今天）
2. 同时启动阿里云 ICP 备案流程（约10-20个工作日）
3. 备案完成后，叠加阿里云 OSS 国内加速

---

## 八、成本估算

| 项目 | 费用 | 备注 |
|------|------|------|
| 域名 `longjiang-ai.com` | ¥78/首年 | 阿里云注册 |
| Cloudflare Pages | ¥0/月 | 免费套餐 |
| 阿里云 OSS（备选） | ¥30/月 | 可选 |
| ICP 备案 | ¥0 | 免费但需时间 |
| **总计/首年** | **¥78** | 纯Cloudflare方案 |

---

## 九、部署检查清单

- [ ] 域名已购买 (`longjiang-ai.com`)
- [ ] 阿里云实名认证完成
- [ ] 37个落地页已改造完成（导航/页脚/CTA）
- [ ] 首页 index.html 已创建
- [ ] robots.txt 已配置
- [ ] sitemap.xml 已生成
- [ ] 404.html 已创建
- [ ] Cloudflare 账户已注册
- [ ] Pages 项目已创建
- [ ] 自定义域名已绑定
- [ ] HTTPS 自动生效（橙色云代理）
- [ ] sitemap 已提交至百度/Google
- [ ] JSON-LD 验证通过（Google Rich Results Test）
- [ ] 移动端适配验证通过

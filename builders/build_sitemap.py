#!/usr/bin/env python3
"""
build_sitemap.py — 自动生成 longjiang-ai.com sitemap.xml

使用：
  python builders/build_sitemap.py

输出：
  sitemap.xml（写入项目根目录），包含：
    - 首页 / 分类页 / 视频页 / 案例页 / 联系页
    - 37个产品落地页（从 output/landing/ 自动扫描）
"""

import os
from datetime import datetime

DOMAIN = "longjiang-ai.com"
LANDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "landing")
EN_DIR = os.path.join(LANDING_DIR, "en")
OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sitemap.xml")

# 固定页面（中文 + 英文）
pages = [
    # 中文
    {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/index.html", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/products/", "priority": "0.9", "changefreq": "daily"},
    {"loc": "/videos/", "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/cases/", "priority": "0.7", "changefreq": "monthly"},
    {"loc": "/contact/", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/about/", "priority": "0.6", "changefreq": "monthly"},
    {"loc": "/service/", "priority": "0.5", "changefreq": "monthly"},
    # 英文
    {"loc": "/en/", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/en/index.html", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/en/products/", "priority": "0.9", "changefreq": "daily"},
    {"loc": "/en/videos/", "priority": "0.8", "changefreq": "weekly"},
    {"loc": "/en/cases/", "priority": "0.7", "changefreq": "monthly"},
    {"loc": "/en/contact/", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/en/about/", "priority": "0.6", "changefreq": "monthly"},
    {"loc": "/en/service/", "priority": "0.5", "changefreq": "monthly"},
]

# 扫描 landing 目录（中文产品页）
if os.path.isdir(LANDING_DIR):
    for fname in sorted(os.listdir(LANDING_DIR)):
        if fname.endswith(".html"):
            name = fname[:-5]
            pages.append({
                "loc": f"/products/{name}.html",
                "priority": "0.8",
                "changefreq": "weekly"
            })

# 扫描 landing/en（英文产品页）
if os.path.isdir(EN_DIR):
    for fname in sorted(os.listdir(EN_DIR)):
        if fname.endswith(".html"):
            name = fname[:-5]
            pages.append({
                "loc": f"/en/products/{name}.html",
                "priority": "0.8",
                "changefreq": "weekly"
            })

today = datetime.now().strftime("%Y-%m-%d")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for p in pages:
    xml += '  <url>\n'
    xml += f'    <loc>https://{DOMAIN}{p["loc"]}</loc>\n'
    xml += f'    <lastmod>{today}</lastmod>\n'
    xml += f'    <changefreq>{p["changefreq"]}</changefreq>\n'
    xml += f'    <priority>{p["priority"]}</priority>\n'
    xml += '  </url>\n'
xml += '</urlset>\n'

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"✅ sitemap.xml generated — {len(pages)} URLs → {OUTPUT}")
print(f"   固定页面: 16 个（中英文各8）")
print(f"   产品落地页: {len(pages) - 16} 个（中英文各37）")

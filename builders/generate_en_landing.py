#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re

LD = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "landing")
OD = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "landing_en")
DM = "longjiang-ai.com"
PH = "18968693691"
EM = "inquiry@longjiang-ai.com"
os.makedirs(OD, exist_ok=True)

# Translation map
TR = {
    "绕线机": "Winding Machine",
    "内绕": "Internal Winding",
    "外绕": "Flyer Winding",
    "双工位": "Double-Station",
    "单工位": "Single-Station",
    "四工位": "Four-Station",
    "六工位": "Six-Station",
    "高速": "High-Speed",
    "多股": "Multi-Strand",
    "经济型": "Economy",
    "标准型": "Standard",
    "磁钢机": "Magnet Inserter",
    "点胶": "Dispensing",
    "插纸机": "Paper Inserter",
    "插签机": "Tag Inserter",
    "分块": "Segmented",
    "内嵌式": "Embedded",
    "表贴": "Surface-Mount",
    "自动": "Automatic",
    "视觉定位": "Vision Positioning",
    "定子": "Stator",
    "转子": "Rotor",
    "伺服": "Servo",
}
TL = sorted(TR.items(), key=lambda x: -len(x[0]))

def tname(name):
    result = name
    for zh, en in TL:
        if zh in result:
            result = result.replace(zh, en)
    result = re.sub(r"\s+", " ", result).strip()
    result = result.replace("_", " ").strip()
    result = re.sub(r"[一-鿿]+$", "", result).strip()
    result = result.rstrip("- _")
    return result or name

def main():
    print("Generating English landing pages...")
    if not os.path.isdir(LD):
        print(f"Error: {LD} not found")
        return
    files = sorted([f for f in os.listdir(LD) if f.endswith(".html")])
    print(f"Found {len(files)} pages")
    for fn in files:
        fp = os.path.join(LD, fn)
        with open(fp, "r", encoding="utf-8") as f:
            html = f.read()
        slug = fn.replace(".html", "")
        en_name = tname(slug)
        # Change language
        html = html.replace('lang="zh-CN"', 'lang="en"')
        # Update title
        html = re.sub(r"<title>.*?</title>", f"<title>{en_name} | Longjiang Auto Equipment</title>", html)
        # Update description
        html = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + en_name + ' - Winding machine manufacturer">', html)
        # Update canonical
        html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://{DM}/en/products/{slug}.html">', html)
        # Add hreflang
        hf_parts = []
        hf_parts.append(f'  <link rel="alternate" hreflang="zh-CN" href="https://{DM}/products/{slug}.html">')
        hf_parts.append(f'  <link rel="alternate" hreflang="en" href="https://{DM}/en/products/{slug}.html">')
        hf_parts.append(f'  <link rel="alternate" hreflang="x-default" href="https://{DM}/products/{slug}.html">')
        hf = '\\n'.join(hf_parts) + '\\n'
        html = html.replace("</head>", hf + "</head>")
        # Replace nav
        nav = f'<nav class="lj-nav" id="ljNav"><div class="lj-nav-inner"><a href="https://{DM}/en/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span class="lj-nav-name">Longjiang Auto</span></a><button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button><ul class="lj-nav-links" id="ljNavLinks"><li><a href="https://{DM}/en/">Home</a></li><li><a href="https://{DM}/en/products/">Products</a></li><li><a href="https://{DM}/en/videos/">Videos</a></li><li><a href="https://{DM}/en/about/">About</a></li><li><a href="https://{DM}/en/contact/" class="lj-nav-cta">Contact</a></li><li><a href="https://{DM}/products/{slug}.html" class="lj-lang-switch"><strong>EN</strong> | 中</a></li></ul></div></nav>'
        html = re.sub(r'<nav class="lj-nav"[^>]*>.*?</nav>', nav, html, count=1, flags=re.DOTALL)
        # Replace footer (simplified inline)
        footer = f'<footer class="lj-footer"><div class="lj-footer-inner"><p>&copy; 2026 Taizhou Longjiang Auto Equipment Co., Ltd. <a href="https://{DM}/en/">Home</a> | <a href="https://{DM}/en/contact/">Contact</a></p></div></footer>'
        html = re.sub(r'<footer class="lj-footer">.*?</footer>', footer, html, count=1, flags=re.DOTALL)
        # Replace floating bar
        cta = f'<div class="lj-float-bar" id="ljFloatBar"><a class="lj-float-item lj-float-phone" href="tel:+86{PH}"><span>Call +86-{PH}</span></a><a class="lj-float-item lj-float-form" href="mailto:{EM}"><span>Email</span></a><a class="lj-float-item lj-float-form" href="https://{DM}/en/contact/"><span>Get Quote</span></a></div>'
        html = re.sub(r'<div class="lj-float-bar"[^>]*>.*?</div>', cta, html, count=1, flags=re.DOTALL)
        # Text replacements
        for zh, en in [("加微信询价", "Email Us"), ("电话咨询", "Call Now"), ("获取方案", "Get Quote"), ("查看参数", "View Specs"), ("功能特性", "Features"), ("关键部件", "Components"), ("适用场景", "Applications")]:
            html = html.replace(zh, en)
        # Write
        op = os.path.join(OD, fn)
        with open(op, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  OK {fn} -> {en_name}")
    print(f"Done! {len(files)} pages -> {OD}")

if __name__ == "__main__":
    main()

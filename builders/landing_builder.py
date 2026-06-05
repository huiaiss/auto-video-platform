#!/usr/bin/env python
"""Landing Page Builder — 设备专属三屏落地页引擎

产出纯静态 HTML（零外部依赖，加载 <2s），
从 products-geo.json 读取 39 个设备数据，逐设备渲染独立落地页。

Usage:
    python -m builders.landing_builder
    # 输出到 output/landing/{model_slug}.html

数据流:
    products-geo.json  ──→  LandingBuilder  ──→  output/landing/*.html
    taizhou_longjiang.json ──→  品牌视觉/联系方式

三屏结构:
    屏1: 视频 + USP + 设备名 + 品牌
    屏2: 参数对比表 + 功能特性 + 关键部件 + 适用场景
    屏3: CTA + 联系方式 + 认证 + Footer
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _slug(text: str, max_len: int = 60) -> str:
    """将设备型号/名称转为安全的文件名 slug。"""
    s = text.strip()
    # 保留字母数字汉字、连字符、下划线、点
    s = re.sub(r'[^\w\-.一-鿿]', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    if not s:
        s = 'device'
    # 截断
    if len(s) > max_len:
        s = s[:max_len].rstrip('_')
    return s


def _read_json(path: str) -> dict:
    """读取 UTF-8 JSON 文件。"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 落地页模板（纯 f-string，无 Jinja2）
# ---------------------------------------------------------------------------

def _render_landing(device: dict, brand: dict) -> str:
    """渲染单个设备的完整落地页 HTML。"""

    # ── 数据提取 ──────────────────────────────────────────────────────
    name = device.get("name", "设备")
    model = device.get("model", "")
    category = device.get("category", "自动化设备")
    summary = device.get("summary", "")

    # 从 summary 提取 USP（取第一句有实质内容的）
    usp = _extract_usp(summary, device)

    specs = device.get("specs", {})
    features = device.get("features", [])
    components = device.get("components", [])
    applications = device.get("applications", [])

    # 品牌信息
    brand_name = brand.get("brand_name", "台州隆江自动化")
    brand_full = brand.get("brand_full_name", "台州隆江自动化设备有限公司")
    slogan = brand.get("slogan", "让绕线更智能")
    location = brand.get("location", "")
    certification = brand.get("certification", "")
    contact_info = brand.get("contact", {})
    vi = brand.get("visual_identity", {})
    primary_color = vi.get("primary_color", "#0057b8")
    secondary_color = vi.get("secondary_color", "#00a8ff")
    bg_gradient = vi.get("bg_gradient", "linear-gradient(135deg, #0a1628, #1a2a4a)")

    contact_phone = device.get("contact", "待填")
    if contact_phone == "待填":
        contact_phone = contact_info.get("phone", "待填")
    contact_address = contact_info.get("address", location)

    # 设备别名（页面标题用）— 避免 model 已包含 name 时的冗余
    if model and name:
        # 如果 model 已经包含 name 中的核心词，只用 model
        if name[:2] in model or name[:4] in model:
            display_name = model
        else:
            display_name = f"{model} {name}"
    elif model:
        display_name = model
    else:
        display_name = name

    # ── JSON-LD ──────────────────────────────────────────────────────
    json_ld = _build_json_ld(device, brand)

    # ── 页面各部分渲染 ──────────────────────────────────────────────
    screen1 = _render_screen1(device, brand, usp, display_name)
    screen2 = _render_screen2(specs, features, components, applications)
    screen3 = _render_screen3(brand, contact_phone, contact_address, display_name)

    # ── 内联 CSS ────────────────────────────────────────────────────
    css = _render_css(primary_color, secondary_color, bg_gradient)

    # ── 内联 JS ─────────────────────────────────────────────────────
    js = _render_js()

    # ── 组装 ─────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">
<meta name="description" content="{_escape_html(usp)} — {_escape_html(brand_full)}">
<meta name="keywords" content="{_escape_html(','.join([name, model, category, brand_name, '自动化设备', '源头工厂']))}">
<meta name="format-detection" content="telephone=yes">
<title>{_escape_html(display_name)} | {_escape_html(brand_full)}</title>
{json_ld}
<style>{css}</style>
</head>
<body>
{screen1}
{screen2}
{screen3}
<script>{js}</script>
</body>
</html>"""
    return html


def _escape_html(text: str) -> str:
    """HTML 转义。"""
    if not isinstance(text, str):
        text = str(text)
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def _extract_usp(summary: str, device: dict) -> str:
    """从 summary 或 features 提取核心卖点（一句话 USP）。"""
    # 优先从 features 第一条
    features = device.get("features", [])
    if features:
        return features[0]

    # 从 summary 提取有意义的部分
    if summary:
        # 按句号、分号、换行切分
        parts = re.split(r'[。；\n]', summary)
        for p in parts:
            p = p.strip()
            # 跳过太短或含"方案书"等无意义内容
            if len(p) > 8 and "方案书" not in p and "设备功能" not in p:
                return p

    # fallback
    return f"{device.get('name', '设备')} — 高精度自动化绕线方案"


def _build_json_ld(device: dict, brand: dict) -> str:
    """构建 JSON-LD 结构化数据（schema.org/Product）。"""
    name = device.get("name", "")
    model = device.get("model", "")
    display_name = f"{model} {name}" if model else name
    brand_name = brand.get("brand_full_name", brand.get("brand_name", ""))
    location = brand.get("location", "")
    phone = brand.get("contact", {}).get("phone", "")
    certification = brand.get("certification", "")
    category = device.get("category", "自动化设备")

    specs = device.get("specs", {})
    features = device.get("features", [])

    # 构建 specs 列表
    spec_items = ""
    for k, v in specs.items():
        spec_items += f"""
          {{"@type":"PropertyValue","name":{json.dumps(k)},"value":{json.dumps(v)}}},"""

    # 构建 feature 列表
    feature_list = [json.dumps(f, ensure_ascii=False) for f in features]

    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": display_name,
        "model": model,
        "description": _extract_usp(device.get("summary", ""), device),
        "category": category,
        "manufacturer": {
            "@type": "Organization",
            "name": brand_name,
            "address": location
        },
        "brand": {
            "@type": "Brand",
            "name": brand.get("brand_name", "")
        },
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {
                "@type": "Organization",
                "name": brand_name
            }
        }
    }
    if certification:
        data["award"] = certification
    if specs:
        data["additionalProperty"] = [
            {"@type": "PropertyValue", "name": k, "value": v}
            for k, v in specs.items()
        ]
    if features:
        data["featureBullet"] = features
    if phone:
        data.setdefault("contactPoint", {})
        data["contactPoint"] = {
            "@type": "ContactPoint",
            "telephone": phone,
            "contactType": "sales"
        }

    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    return f"""<script type="application/ld+json">
{json_str}
</script>"""


# ---------------------------------------------------------------------------
# 屏1 — 视频 + USP + 设备名
# ---------------------------------------------------------------------------

def _render_screen1(device: dict, brand: dict, usp: str, display_name: str) -> str:
    brand_name = brand.get("brand_name", "")
    brand_full = brand.get("brand_full_name", "")
    slogan = brand.get("slogan", "")
    location = brand.get("location", "")

    return f"""<!-- ═══ 屏1：视频 + USP ═══ -->
<section id="screen1" class="screen">
  <div class="video-bg">
    <video class="bg-video" autoplay muted loop playsinline
           poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='800' height='600' viewBox='0 0 800 600'%3E%3Crect width='800' height='600' fill='%230a1628'/%3E%3Ctext x='400' y='300' fill='%2300a8ff' font-size='32' text-anchor='middle' font-family='sans-serif'%3E{_escape_html(display_name)}%3C/text%3E%3C/svg%3E">
      <source src="about:blank" type="video/mp4">
    </video>
    <div class="video-overlay"></div>
  </div>

  <div class="screen-content">
    <div class="brand-tag">
      <span class="brand-logo-dot"></span>
      <span class="brand-name">{_escape_html(brand_name)}</span>
      <span class="brand-location">| {_escape_html(location)}</span>
    </div>

    <h1 class="device-title">{_escape_html(display_name)}</h1>
    <p class="usp-line">{_escape_html(usp)}</p>

    <div class="slogan-bar">{_escape_html(slogan)}</div>
  </div>

  <div class="scroll-hint">
    <span class="scroll-text">向下滚动</span>
    <div class="scroll-arrow">
      <svg width="24" height="40" viewBox="0 0 24 40" fill="none">
        <rect x="1" y="1" width="22" height="38" rx="11" stroke="rgba(255,255,255,0.4)" stroke-width="2"/>
        <circle cx="12" cy="13" r="3" fill="rgba(255,255,255,0.6)">
          <animate attributeName="cy" values="13;25;13" dur="2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
        </circle>
      </svg>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------------------
# 屏2 — 参数 + 特性 + 部件 + 场景
# ---------------------------------------------------------------------------

def _render_screen2(specs: dict, features: list, components: list, applications: list) -> str:
    # 规格参数表
    specs_rows = ""
    for k, v in specs.items():
        specs_rows += f"""
          <tr><td class="spec-key">{_escape_html(k)}</td><td class="spec-val">{_escape_html(v)}</td></tr>"""

    # 功能特性
    features_html = ""
    for f in features:
        features_html += f"""
          <li class="feature-item"><span class="check-icon">✓</span> {_escape_html(f)}</li>"""

    # 关键部件
    comps_html = ""
    for c in components:
        comps_html += f"""<span class="component-chip">{_escape_html(c)}</span>"""

    # 适用场景
    apps_html = ""
    for a in applications:
        apps_html += f"""<span class="app-chip">{_escape_html(a)}</span>"""

    return f"""<!-- ═══ 屏2：参数 + 特性 + 部件 + 场景 ═══ -->
<section id="screen2" class="screen">
  <div class="screen2-bg"></div>
  <div class="screen-content">

    <h2 class="section-title">技术规格</h2>
    <div class="specs-table-wrapper">
      <table class="specs-table">
        <thead>
          <tr><th>参数</th><th>规格</th></tr>
        </thead>
        <tbody>
          {specs_rows}
        </tbody>
      </table>
    </div>

    <div class="features-block">
      <h2 class="section-title">功能特性</h2>
      <ul class="features-list">
        {features_html}
      </ul>
    </div>

    <div class="components-block">
      <h2 class="section-title">关键部件</h2>
      <div class="chips-wrapper">
        {comps_html}
      </div>
    </div>

    <div class="applications-block">
      <h2 class="section-title">适用场景</h2>
      <div class="chips-wrapper">
        {apps_html}
      </div>
    </div>

  </div>
</section>"""


# ---------------------------------------------------------------------------
# 屏3 — CTA + 联系方式
# ---------------------------------------------------------------------------

def _render_screen3(brand: dict, phone: str, address: str, display_name: str) -> str:
    brand_name = brand.get("brand_name", "")
    brand_full = brand.get("brand_full_name", "")
    slogan = brand.get("slogan", "")
    certification = brand.get("certification", "")
    core_patent = brand.get("core_patent", "")
    industry = brand.get("industry", "")
    employees = brand.get("employees", "")
    website = brand.get("contact", {}).get("website", "")

    contact_phone = phone if phone != "待填" else "咨询热线：请来电商议"
    phone_digits = re.sub(r'\D', '', phone) if phone != "待填" else ""

    return f"""<!-- ═══ 屏3：CTA + 联系方式 ═══ -->
<section id="screen3" class="screen">
  <div class="screen3-bg"></div>
  <div class="screen-content">

    <div class="cta-block">
      <h2 class="cta-title">获取专属选型方案</h2>
      <p class="cta-sub">技术工程师 1 对 1 对接 · 免费提供样机打样</p>

      <div class="cta-buttons">
        <a class="cta-btn cta-primary" href="tel:{_escape_html(phone_digits)}" rel="nofollow">
          <svg class="cta-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
          {_escape_html(contact_phone)}
        </a>

        <button class="cta-btn cta-secondary" id="copyWechatBtn" onclick="copyWechat()">
          <svg class="cta-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8.5 11C9.33 11 10 10.33 10 9.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm7 0c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zM12 2C6.48 2 2 6.48 2 12c0 1.88.54 3.63 1.48 5.11L2 22l4.92-1.48C8.36 21.46 10.12 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.54 0-3-.42-4.25-1.15l-.3-.18-2.92.87.88-2.85-.2-.32C4.42 15.35 4 13.78 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/></svg>
          加微信询价
        </button>

        <a class="cta-btn cta-outline" href="#screen1" onclick="smoothScroll(0)">
          <svg class="cta-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l4.59-4.58L18 11l-6 6z"/></svg>
          查看参数
        </a>
      </div>
    </div>

    <div class="company-info">
      <div class="company-card">
        <div class="company-name">{_escape_html(brand_full)}</div>
        <div class="company-meta">
          <div class="meta-item">
            <span class="meta-label">行业</span>
            <span class="meta-value">{_escape_html(industry)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">规模</span>
            <span class="meta-value">{_escape_html(employees)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">地址</span>
            <span class="meta-value">{_escape_html(address)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">认证</span>
            <span class="meta-value cert-badge">{_escape_html(certification)}</span>
          </div>
        </div>
      </div>
    </div>

    <footer class="landing-footer">
      <p>© {_escape_html(brand_full)} &nbsp;|&nbsp; {_escape_html(slogan)}</p>
      <p class="footer-tagline">制造业AI询盘工厂 — 让每一台设备被精准找到</p>
    </footer>

  </div>
</section>"""


# ---------------------------------------------------------------------------
# 内联 CSS（深色工业风 · 移动优先 · 自适应）
# ---------------------------------------------------------------------------

def _render_css(primary: str, secondary: str, bg_gradient: str) -> str:
    return f"""/* ═══════════════════════════════════════════════════
   落地页样式 — 深色工业风 · 移动优先
   品牌色: {primary} / {secondary}
   ═══════════════════════════════════════════════════ */

*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}

:root{{
  --primary:{primary};
  --secondary:{secondary};
  --bg-gradient:{bg_gradient};
  --bg-dark:#0a1628;
  --bg-card:#0f1d35;
  --text-primary:#f0f4ff;
  --text-secondary:#8a9bb5;
  --text-muted:#5a6d8a;
  --border-color:rgba(0,87,184,0.25);
  --glow:0 0 30px rgba(0,168,255,0.12);
  --radius:12px;
}}

html{{
  scroll-behavior:smooth;
  -webkit-tap-highlight-color:transparent;
}}

body{{
  font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg-dark);
  color:var(--text-primary);
  line-height:1.6;
  overflow-x:hidden;
  width:100%;
}}

/* ── 三屏通用 ── */
.screen{{
  min-height:100vh;
  min-height:100dvh;
  width:100%;
  display:flex;
  align-items:center;
  justify-content:center;
  position:relative;
  overflow:hidden;
  padding:24px 20px;
}}

.screen-content{{
  position:relative;
  z-index:2;
  width:100%;
  max-width:480px;
  margin:0 auto;
}}

.section-title{{
  font-size:20px;
  font-weight:700;
  color:var(--secondary);
  margin-bottom:16px;
  letter-spacing:2px;
  position:relative;
  display:inline-block;
}}
.section-title::after{{
  content:'';
  position:absolute;
  bottom:-4px;
  left:0;
  width:100%;
  height:2px;
  background:linear-gradient(90deg,var(--primary),transparent);
}}

/* ── 屏1 ── */
.video-bg{{
  position:absolute;
  inset:0;
  z-index:0;
}}
.bg-video{{
  width:100%;
  height:100%;
  object-fit:cover;
  opacity:0.3;
}}
.video-overlay{{
  position:absolute;
  inset:0;
  background:linear-gradient(180deg,rgba(10,22,40,0.3) 0%,rgba(10,22,40,0.92) 70%,#0a1628 100%);
  z-index:1;
}}

.brand-tag{{
  display:flex;
  align-items:center;
  gap:8px;
  margin-bottom:20px;
  font-size:13px;
  color:var(--text-secondary);
  letter-spacing:1px;
}}
.brand-logo-dot{{
  width:8px;height:8px;
  background:var(--secondary);
  border-radius:50%;
  display:inline-block;
  box-shadow:0 0 12px var(--secondary);
}}
.brand-name{{
  color:var(--text-primary);
  font-weight:600;
}}
.brand-location{{
  color:var(--text-muted);
}}

.device-title{{
  font-size:28px;
  font-weight:800;
  line-height:1.2;
  margin-bottom:16px;
  background:linear-gradient(135deg,#fff 30%,var(--secondary));
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
}}

.usp-line{{
  font-size:16px;
  color:var(--text-secondary);
  line-height:1.5;
  margin-bottom:24px;
  padding-left:16px;
  border-left:3px solid var(--secondary);
}}

.slogan-bar{{
  display:inline-block;
  padding:8px 20px;
  background:rgba(0,87,184,0.15);
  border:1px solid rgba(0,87,184,0.3);
  border-radius:20px;
  font-size:13px;
  color:var(--text-secondary);
  letter-spacing:2px;
}}

.scroll-hint{{
  position:absolute;
  bottom:36px;
  left:50%;
  transform:translateX(-50%);
  z-index:3;
  display:flex;
  flex-direction:column;
  align-items:center;
  gap:8px;
  animation:fadeInUp 1.5s ease-out 1s both;
}}
.scroll-text{{
  font-size:11px;
  color:var(--text-muted);
  letter-spacing:2px;
  text-transform:uppercase;
}}

@keyframes fadeInUp{{
  from{{opacity:0;transform:translateY(16px)}}
  to{{opacity:1;transform:translateY(0)}}
}}

/* ── 屏2 ── */
.screen2-bg{{
  position:absolute;
  inset:0;
  background:var(--bg-dark);
  z-index:0;
}}
.screen2-bg::before{{
  content:'';
  position:absolute;
  top:-30%;
  right:-20%;
  width:400px;height:400px;
  background:radial-gradient(circle,rgba(0,87,184,0.08),transparent 70%);
  pointer-events:none;
}}

.specs-table-wrapper{{
  margin-bottom:32px;
  overflow-x:auto;
  -webkit-overflow-scrolling:touch;
}}
.specs-table{{
  width:100%;
  border-collapse:collapse;
  font-size:14px;
}}
.specs-table thead th{{
  background:rgba(0,87,184,0.2);
  padding:12px 14px;
  text-align:left;
  font-weight:600;
  color:var(--secondary);
  font-size:13px;
  letter-spacing:1px;
  border-bottom:2px solid var(--primary);
}}
.specs-table tbody td{{
  padding:11px 14px;
  border-bottom:1px solid var(--border-color);
  vertical-align:top;
}}
.specs-table .spec-key{{
  color:var(--text-muted);
  font-weight:500;
  width:40%;
  white-space:nowrap;
}}
.specs-table .spec-val{{
  color:var(--text-primary);
  font-weight:500;
}}

.features-block,
.components-block,
.applications-block{{
  margin-bottom:28px;
}}

.features-list{{
  list-style:none;
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:8px 12px;
}}
.feature-item{{
  font-size:13px;
  color:var(--text-secondary);
  display:flex;
  align-items:flex-start;
  gap:6px;
  padding:6px 10px;
  background:rgba(0,87,184,0.06);
  border-radius:6px;
  border-left:2px solid rgba(0,168,255,0.2);
}}
.check-icon{{
  color:var(--secondary);
  font-weight:700;
  flex-shrink:0;
}}

.chips-wrapper{{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
}}
.component-chip{{
  display:inline-block;
  padding:6px 14px;
  background:rgba(0,87,184,0.12);
  border:1px solid rgba(0,87,184,0.2);
  border-radius:20px;
  font-size:12px;
  color:var(--text-secondary);
  letter-spacing:0.5px;
}}
.app-chip{{
  display:inline-block;
  padding:7px 16px;
  background:linear-gradient(135deg,rgba(0,87,184,0.15),rgba(0,168,255,0.08));
  border:1px solid rgba(0,168,255,0.15);
  border-radius:20px;
  font-size:12px;
  color:var(--secondary);
  letter-spacing:0.5px;
}}

/* ── 屏3 ── */
.screen3-bg{{
  position:absolute;
  inset:0;
  background:{bg_gradient};
  z-index:0;
}}

.cta-block{{
  text-align:center;
  margin-bottom:36px;
}}
.cta-title{{
  font-size:26px;
  font-weight:800;
  margin-bottom:8px;
  background:linear-gradient(135deg,#fff,var(--secondary));
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
}}
.cta-sub{{
  font-size:14px;
  color:var(--text-muted);
  margin-bottom:28px;
}}

.cta-buttons{{
  display:flex;
  flex-direction:column;
  gap:12px;
  align-items:stretch;
  max-width:360px;
  margin:0 auto;
}}

.cta-btn{{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  padding:16px 24px;
  border-radius:var(--radius);
  font-size:16px;
  font-weight:600;
  text-decoration:none;
  cursor:pointer;
  transition:all 0.25s ease;
  border:none;
  font-family:inherit;
  letter-spacing:1px;
}}
.cta-btn:active{{
  transform:scale(0.97);
}}

.cta-primary{{
  background:linear-gradient(135deg,var(--primary),var(--secondary));
  color:#fff;
  box-shadow:0 4px 24px rgba(0,87,184,0.35);
}}
.cta-primary:hover{{
  box-shadow:0 6px 32px rgba(0,87,184,0.5);
  transform:translateY(-1px);
}}

.cta-secondary{{
  background:rgba(255,255,255,0.06);
  color:var(--text-primary);
  border:1px solid rgba(255,255,255,0.12);
  backdrop-filter:blur(8px);
}}
.cta-secondary:hover{{
  background:rgba(255,255,255,0.1);
  border-color:var(--secondary);
}}

.cta-outline{{
  background:transparent;
  color:var(--text-secondary);
  border:1px solid var(--border-color);
  font-size:14px;
  padding:12px 24px;
}}
.cta-outline:hover{{
  border-color:var(--text-muted);
  color:var(--text-primary);
}}

.cta-icon{{
  flex-shrink:0;
}}

/* ── 公司信息 ── */
.company-info{{
  margin-bottom:24px;
}}
.company-card{{
  background:rgba(255,255,255,0.03);
  border:1px solid var(--border-color);
  border-radius:var(--radius);
  padding:20px;
}}
.company-name{{
  font-size:16px;
  font-weight:700;
  color:var(--text-primary);
  margin-bottom:14px;
  padding-bottom:10px;
  border-bottom:1px solid var(--border-color);
}}
.company-meta{{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:10px;
}}
.meta-item{{
  display:flex;
  flex-direction:column;
  gap:2px;
}}
.meta-label{{
  font-size:11px;
  color:var(--text-muted);
  text-transform:uppercase;
  letter-spacing:1px;
}}
.meta-value{{
  font-size:13px;
  color:var(--text-secondary);
}}
.cert-badge{{
  color:var(--secondary);
  font-weight:600;
}}

/* ── Footer ── */
.landing-footer{{
  text-align:center;
  padding:20px 0 10px;
  border-top:1px solid var(--border-color);
}}
.landing-footer p{{
  font-size:12px;
  color:var(--text-muted);
  line-height:1.8;
}}
.footer-tagline{{
  font-size:11px;
  opacity:0.5;
  letter-spacing:1px;
}}

/* ── Toast 通知 ── */
.toast{{
  position:fixed;
  bottom:80px;
  left:50%;
  transform:translateX(-50%) translateY(20px);
  background:rgba(0,87,184,0.92);
  color:#fff;
  padding:12px 24px;
  border-radius:8px;
  font-size:14px;
  z-index:999;
  opacity:0;
  transition:all 0.35s ease;
  pointer-events:none;
  backdrop-filter:blur(12px);
  border:1px solid rgba(0,168,255,0.2);
  white-space:nowrap;
}}
.toast.show{{
  opacity:1;
  transform:translateX(-50%) translateY(0);
}}

/* ── 响应式（平板 / 桌面） ── */
@media(min-width:768px){{
  .screen{{padding:32px 40px;}}
  .screen-content{{max-width:640px;}}
  .device-title{{font-size:36px;}}
  .usp-line{{font-size:18px;}}
  .cta-buttons{{flex-direction:row;flex-wrap:wrap;max-width:100%;justify-content:center;}}
  .cta-btn{{flex:0 1 auto;min-width:180px;}}
  .features-list{{grid-template-columns:1fr 1fr 1fr;}}
  .company-meta{{grid-template-columns:1fr 1fr;}}
}}

@media(min-width:1200px){{
  .screen{{padding:48px 64px;}}
  .screen-content{{max-width:800px;}}
  .device-title{{font-size:44px;}}
  .usp-line{{font-size:20px;padding-left:24px;}}
  .section-title{{font-size:24px;}}
  .specs-table{{font-size:15px;}}
  .features-list{{grid-template-columns:1fr 1fr 1fr 1fr;}}
}}

/* ── 超宽屏适配 ── */
@media(min-width:1920px){{
  .screen-content{{max-width:960px;}}
  .device-title{{font-size:52px;}}
}}

/* ── 手机横屏修正 ── */
@media(max-height:600px) and (orientation:landscape){{
  .screen{{min-height:120vh;padding:32px 40px;}}
  .device-title{{font-size:22px;}}
  .scroll-hint{{display:none;}}
}}
"""


# ---------------------------------------------------------------------------
# 内联 JS（轻量交互）
# ---------------------------------------------------------------------------

def _render_js() -> str:
    return """/* ═══════════════════════════════════════════════════
   落地页交互 — 零外部依赖
   ═══════════════════════════════════════════════════ */

(function() {
  'use strict';

  // 平滑滚动
  window.smoothScroll = function(targetY) {
    window.scrollTo({ top: targetY, behavior: 'smooth' });
  };

  // 点击箭头向下翻一屏
  document.addEventListener('DOMContentLoaded', function() {
    var screens = document.querySelectorAll('.screen');
    var scrollHint = document.querySelector('.scroll-hint');
    if (scrollHint) {
      scrollHint.addEventListener('click', function(e) {
        e.stopPropagation();
        var nextScreen = screens[1];
        if (nextScreen) {
          nextScreen.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }

    // 视频降噪监听：如果真实视频加载失败，显示纯色背景
    var video = document.querySelector('.bg-video');
    if (video) {
      video.addEventListener('error', function() {
        // 视频源不可用时，保持现有渐变背景
        this.style.display = 'none';
      });
    }
  });

  // 复制微信号（演示用，实际可配置）
  window.copyWechat = function() {
    var wechat = 'ljzdh888';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(wechat).then(function() {
        showToast('微信号 ' + wechat + ' 已复制，打开微信添加');
      }).catch(function() {
        fallbackCopy(wechat);
      });
    } else {
      fallbackCopy(wechat);
    }
  };

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('微信号 ' + text + ' 已复制，打开微信添加');
    } catch(e) {
      showToast('请截图保存微信号：' + text);
    }
    document.body.removeChild(ta);
  }

  function showToast(msg) {
    var toast = document.querySelector('.toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(function() {
      toast.classList.remove('show');
    }, 3000);
  }

})();
"""


# ---------------------------------------------------------------------------
# 主构建类
# ---------------------------------------------------------------------------

class LandingBuilder:
    """设备落地页构建器。"""

    def __init__(self, brand_config_path: str = None, product_data_path: str = None):
        if brand_config_path is None:
            brand_config_path = os.path.join(ROOT, "configs", "brands", "taizhou_longjiang.json")
        if product_data_path is None:
            product_data_path = os.path.join(ROOT, "configs", "brands", "products-geo.json")

        self.brand = _read_json(brand_config_path)
        self.product_data = _read_json(product_data_path)
        self.output_dir = os.path.join(ROOT, "output", "landing")

    def build_all(self) -> list:
        """为所有设备生成落地页，返回生成的文件路径列表。"""
        os.makedirs(self.output_dir, exist_ok=True)

        products = self.product_data.get("products", {})
        generated = []

        for category_name, device_list in products.items():
            for device in device_list:
                if not isinstance(device, dict):
                    continue
                filepath = self._build_one(device)
                if filepath:
                    generated.append(filepath)

        return generated

    def build_by_model(self, model_keyword: str) -> str:
        """按型号关键词生成单个设备落地页（用于验证）。"""
        products = self.product_data.get("products", {})
        for device_list in products.values():
            for device in device_list:
                model = device.get("model", "") + device.get("name", "")
                if model_keyword.lower() in model.lower():
                    return self._build_one(device)
        raise ValueError(f"未找到型号包含 '{model_keyword}' 的设备")

    def _build_one(self, device: dict) -> str:
        """为单个设备生成 HTML 文件。"""
        model = device.get("model", "") or device.get("name", "未知设备")
        slug = _slug(model)
        html = _render_landing(device, self.brand)

        filepath = os.path.join(self.output_dir, f"{slug}.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        name = device.get("name", "")
        print(f"  ✓ {model or name} → {filepath}")
        return filepath


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    """CLI: python -m builders.landing_builder [model_keyword]"""
    builder = LandingBuilder()

    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"🔍 按关键词 '{keyword}' 生成本落地页...")
        try:
            path = builder.build_by_model(keyword)
            print(f"\n✅ 生成完成: {path}")
            print(f"   file:///{path.replace(os.sep, '/')}")
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)
    else:
        print(f"🏭 正在为全部 {builder.product_data.get('total_products', 39)} 个设备生成落地页...")
        files = builder.build_all()
        print(f"\n✅ 已生成 {len(files)} 个落地页:")
        print(f"   输出目录: {builder.output_dir}")
        print(f"   打开示例: file:///{files[0].replace(os.sep, '/')}" if files else "   无文件生成")

    # 输出文件体积检查
    output_dir = builder.output_dir
    if os.path.isdir(output_dir):
        total_size = 0
        for f in os.listdir(output_dir):
            fp = os.path.join(output_dir, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
        print(f"\n📊 输出目录总大小: {total_size/1024:.1f} KB")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
patch_landing.py — 批量改造37个落地页：统一中英双语导航/页脚/询盘按钮

操作：
  1. 注入统一顶部导航栏（中英双语标签 + 语言切换 + 产品下拉）
  2. 替换尾部为双语公司信息+栏目导航+版权
  3. 注入固定底部询盘栏（电话+微信+方案，中英双语）
  4. 补充 canonical URL / hreflang / Open Graph / 更新 JSON-LD
  5. 注入语言切换交互脚本

用法：
  python builders/patch_landing.py           # 37个中文页 + 37个英文页
  python builders/patch_landing.py --dry-run # 预览模式

输出：
  中文页直接改写 output/landing/*.html
  英文页写入 output/landing/en/*.html
"""

import os
import re
import json
import sys
import shutil
from datetime import datetime

# ── 配置 ────────────────────────────────────────────────────
LANDING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "landing")
DOMAIN = "longjiang-ai.com"
BRAND_CN = "台州隆江自动化"
BRAND_EN = "Longjiang Automation"
BRAND_FULL_CN = "台州隆江自动化设备有限公司"
BRAND_FULL_EN = "Taizhou Longjiang Automation Equipment Co., Ltd."
PHONE = "18968693691"
WECHAT = "ljzdh888"
ADDRESS_CN = "浙江台州椒江区刘洋工业园区"
ADDRESS_EN = "Liuyang Industrial Park, Jiaojiang District, Taizhou, Zhejiang"
SLOGAN_CN = "让绕线更智能"
SLOGAN_EN = "Smarter Winding Solutions"
DRY_RUN = False

# ── 双语标签映射 ──────────────────────────────────────────
L10N = {
    "brand": (BRAND_CN, BRAND_EN),
    "brand_full": (BRAND_FULL_CN, BRAND_FULL_EN),
    "slogan": (SLOGAN_CN, SLOGAN_EN),
    "address": (ADDRESS_CN, ADDRESS_EN),
    "home": ("首页", "Home"),
    "products": ("产品", "Products"),
    "videos": ("视频", "Videos"),
    "cases": ("案例", "Cases"),
    "about": ("关于", "About"),
    "contact": ("联系", "Contact"),
    "all_products": ("全部产品", "All Products"),
    "winding_machine": ("绕线机", "Winding Machine"),
    "magnet_machine": ("磁钢机", "Magnet Machine"),
    "paper_inserter": ("插纸机", "Paper Inserter"),
    "other_equip": ("其他设备", "Other Equipment"),
    "phone_consult": ("电话咨询", "Call Us"),
    "wechat_inquiry": ("微信询价", "WeChat"),
    "get_solution": ("获取方案", "Get Solution"),
    "products_center": ("产品中心", "Products"),
    "about_us": ("关于我们", "About Us"),
    "service_support": ("服务支持", "Service"),
    "contact_info": ("联系方式", "Contact"),
    "company_profile": ("公司介绍", "Company"),
    "customer_cases": ("客户案例", "Cases"),
    "service_commitment": ("服务承诺", "Service"),
    "copyright_tagline": ("制造业AI询盘工厂 — 让每一台设备被精准找到",
                          "AI-Powered Inquiry Engine — Helping Your Machines Get Found"),
    "factory_tag": ("源头工厂 · 省级科技型企业", "Factory Direct · Provincial Tech Enterprise"),
    "free_sample": ("免费样机打样", "Free Sample Testing"),
    "tech_consult": ("技术工程师 1 对 1 对接", "1-on-1 Technical Consultation"),
}

def t(key):
    """返回 (cn, en) 元组"""
    return L10N.get(key, (str(key), str(key)))

# ── 统一导航栏 HTML（双语） ──────────────────────────────
def make_nav_html(is_en=False):
    """生成导航栏 HTML，is_en=True 时使用英文"""
    home_zh, home_en = t("home")
    prod_zh, prod_en = t("products")
    vid_zh, vid_en = t("videos")
    case_zh, case_en = t("cases")
    abt_zh, abt_en = t("about")
    ctc_zh, ctc_en = t("contact")
    all_zh, all_en = t("all_products")
    wm_zh, wm_en = t("winding_machine")
    mm_zh, mm_en = t("magnet_machine")
    pi_zh, pi_en = t("paper_inserter")
    oe_zh, oe_en = t("other_equip")
    brand_zh, brand_en = t("brand")

    if is_en:
        brand_label = brand_en
        home_link = f"https://{DOMAIN}/en/"
        prod_link = f"https://{DOMAIN}/en/products/"
        vid_link = f"https://{DOMAIN}/en/videos/"
        case_link = f"https://{DOMAIN}/en/cases/"
        abt_link = f"https://{DOMAIN}/en/about/"
        ctc_link = f"https://{DOMAIN}/en/contact/"
        toggle_link = "javascript:toggleLang()"
        toggle_text = "中文"
        nav_links = [
            (home_link, f"{home_en}"),
            None,  # dropdown marker
            (vid_link, f"{vid_en}"),
            (case_link, f"{case_en}"),
            (abt_link, f"{abt_en}"),
            (ctc_link, f"{ctc_en}", "lj-nav-cta"),
        ]
        dropdown_items = [
            (f"https://{DOMAIN}/en/products/", all_en),
            (f"https://{DOMAIN}/en/products/?cat={wm_en}", wm_en),
            (f"https://{DOMAIN}/en/products/?cat={mm_en}", mm_en),
            (f"https://{DOMAIN}/en/products/?cat={pi_en}", pi_en),
            (f"https://{DOMAIN}/en/products/?cat={oe_en}", oe_en),
        ]
    else:
        brand_label = brand_zh
        home_link = f"https://{DOMAIN}/"
        prod_link = f"https://{DOMAIN}/products/"
        vid_link = f"https://{DOMAIN}/videos/"
        case_link = f"https://{DOMAIN}/cases/"
        abt_link = f"https://{DOMAIN}/about/"
        ctc_link = f"https://{DOMAIN}/contact/"
        toggle_link = "javascript:toggleLang()"
        toggle_text = "English"
        nav_links = [
            (home_link, f"{home_zh}"),
            None,
            (vid_link, f"{vid_zh}"),
            (case_link, f"{case_zh}"),
            (abt_link, f"{abt_zh}"),
            (ctc_link, f"{ctc_zh}", "lj-nav-cta"),
        ]
        dropdown_items = [
            (f"https://{DOMAIN}/products/", all_zh),
            (f"https://{DOMAIN}/products/?cat=绕线机", wm_zh),
            (f"https://{DOMAIN}/products/?cat=磁钢机", mm_zh),
            (f"https://{DOMAIN}/products/?cat=插纸机", pi_zh),
            (f"https://{DOMAIN}/products/?cat=其他", oe_zh),
        ]

    # 构建导航HTML
    links_html = ""
    for item in nav_links:
        if item is None:
            # 产品下拉菜单
            dd_items = ""
            for dd_link, dd_label in dropdown_items:
                dd_items += f'          <li><a href="{dd_link}">{dd_label}</a></li>\n'
            links_html += f'''      <li class="lj-dropdown">
        <a href="javascript:void(0)">{prod_zh if not is_en else prod_en} <span class="lj-dropdown-arrow">▼</span></a>
        <ul class="lj-dropdown-menu">
{dd_items}        </ul>
      </li>
'''
        else:
            link, label = item[0], item[1]
            cls = f' class="{item[2]}"' if len(item) > 2 else ""
            links_html += f'      <li><a href="{link}"{cls}>{label}</a></li>\n'

    return f'''<!-- ═══ 统一导航栏（{"EN" if is_en else "CN"}） ═══ -->
<nav class="lj-nav" id="ljNav">
  <div class="lj-nav-inner">
    <a href="{home_link}" class="lj-nav-brand">
      <span class="lj-nav-dot"></span>
      <span class="lj-nav-name">{brand_label}</span>
    </a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <ul class="lj-nav-links" id="ljNavLinks">
{links_html}      <li><a href="{toggle_link}" class="lj-nav-lang" id="ljLangToggle">🌐 {toggle_text}</a></li>
    </ul>
  </div>
</nav>
'''

# ── 统一页脚 HTML（双语） ─────────────────────────────────
def make_footer_html(is_en=False):
    """生成页脚 HTML"""
    pc_zh, pc_en = t("products_center")
    au_zh, au_en = t("about_us")
    ci_zh, ci_en = t("contact_info")
    cp_zh, cp_en = t("company_profile")
    cc_zh, cc_en = t("customer_cases")
    sc_zh, sc_en = t("service_commitment")
    wm_zh, wm_en = t("winding_machine")
    mm_zh, mm_en = t("magnet_machine")
    pi_zh, pi_en = t("paper_inserter")
    all_zh, all_en = t("all_products")
    brand_zh, brand_en = t("brand")
    brand_full_zh, brand_full_en = t("brand_full")
    slogan_zh, slogan_en = t("slogan")
    addr_zh, addr_en = t("address")
    tag_zh, tag_en = t("copyright_tagline")

    if is_en:
        domain = f"https://{DOMAIN}/en"
        col1_title = pc_en
        col1_items = [
            (f"{domain}/products/?cat={wm_en}", wm_en),
            (f"{domain}/products/?cat={mm_en}", mm_en),
            (f"{domain}/products/?cat={pi_en}", pi_en),
            (f"{domain}/products/", all_en),
        ]
        col2_title = au_en
        col2_items = [
            (f"{domain}/about/", cp_en),
            (f"{domain}/cases/", cc_en),
            (f"{domain}/service/", sc_en),
        ]
        col3_title = ci_en
        col3_extra = ADDRESS_EN
        brand_name = brand_en
        brand_full = brand_full_en
        slogan = slogan_en
        tagline = tag_en
        year = datetime.now().year
    else:
        domain = f"https://{DOMAIN}"
        col1_title = pc_zh
        col1_items = [
            (f"{domain}/products/?cat=绕线机", wm_zh),
            (f"{domain}/products/?cat=磁钢机", mm_zh),
            (f"{domain}/products/?cat=插纸机", pi_zh),
            (f"{domain}/products/", all_zh),
        ]
        col2_title = au_zh
        col2_items = [
            (f"{domain}/about/", cp_zh),
            (f"{domain}/cases/", cc_zh),
            (f"{domain}/service/", sc_zh),
        ]
        col3_title = ci_zh
        col3_extra = ADDRESS_CN
        brand_name = brand_zh
        brand_full = brand_full_zh
        slogan = slogan_zh
        tagline = tag_zh
        year = datetime.now().year

    # 构建列
    col1_html = ""
    for link, label in col1_items:
        col1_html += f'          <li><a href="{link}">{label}</a></li>\n'
    col2_html = ""
    for link, label in col2_items:
        col2_html += f'          <li><a href="{link}">{label}</a></li>\n'

    return f'''<!-- ═══ 统一页脚（{"EN" if is_en else "CN"}） ═══ -->
<footer class="lj-footer">
  <div class="lj-footer-inner">
    <div class="lj-footer-cols">
      <div class="lj-footer-col">
        <h4>{col1_title}</h4>
        <ul>
{col1_html}        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>{col2_title}</h4>
        <ul>
{col2_html}        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>{col3_title}</h4>
        <ul class="lj-footer-contact">
          <li>📞 <a href="tel:{PHONE}">{PHONE}</a></li>
          <li>✉ {"微信: " + WECHAT if not is_en else "WeChat: " + WECHAT}</li>
          <li>📍 {col3_extra}</li>
        </ul>
      </div>
    </div>
    <div class="lj-footer-bottom">
      <p>© {year} {brand_full} &nbsp;|&nbsp; {slogan}</p>
      <p class="lj-footer-tagline">{tagline}</p>
    </div>
  </div>
</footer>
'''

# ── 浮动询盘栏 HTML（手机底部固定 + 桌面右下角） ────────────
def make_float_cta_html(is_en=False):
    """生成浮动询盘栏"""
    phone_zh, phone_en = t("phone_consult")
    wechat_zh, wechat_en = t("wechat_inquiry")
    sol_zh, sol_en = t("get_solution")
    prefix = "/en" if is_en else ""
    phone = phone_en if is_en else phone_zh
    wechat = wechat_en if is_en else wechat_zh
    solution = sol_en if is_en else sol_zh
    return f'''<!-- FloatCTA {"EN" if is_en else "CN"} -->
<div class="lj-float-bar" id="ljFloatBar">
  <a class="lj-float-item lj-float-phone" href="tel:{PHONE}">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
    <span>{phone}</span>
  </a>
  <button class="lj-float-item lj-float-wechat" onclick="copyWechatFloat()">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8.5 11C9.33 11 10 10.33 10 9.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm7 0c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zM12 2C6.48 2 2 6.48 2 12c0 1.88.54 3.63 1.48 5.11L2 22l4.92-1.48C8.36 21.46 10.12 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.54 0-3-.42-4.25-1.15l-.3-.18-2.92.87.88-2.85-.2-.32C4.42 15.35 4 13.78 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/></svg>
    <span>{wechat}</span>
  </a>
  <a class="lj-float-item lj-float-form" href="https://{DOMAIN}{prefix}/contact/">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM6 10h2v2H6zm0 4h8v2H6zm10 0h2v2h-2zm-6-4h8v2h-8z"/></svg>
    <span>{solution}</span>
  </a>
</div>'''

# ── 统一样式（注入到每个页面 <style> 末尾） ─────────────────
NAV_STYLES = """
/* ── 统一导航栏 ── */
.lj-nav{position:sticky;top:0;z-index:100;background:rgba(10,22,40,0.95);backdrop-filter:blur(12px);border-bottom:1px solid rgba(0,87,184,0.2);width:100%;}
.lj-nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:0 20px;height:56px;}
.lj-nav-brand{display:flex;align-items:center;gap:8px;text-decoration:none;font-weight:700;font-size:16px;color:#f0f4ff;flex-shrink:0;}
.lj-nav-dot{width:8px;height:8px;background:#00a8ff;border-radius:50%;display:inline-block;box-shadow:0 0 12px #00a8ff;}
.lj-nav-name{white-space:nowrap;}
.lj-nav-toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-direction:column;gap:4px;}
.lj-nav-toggle span{display:block;width:22px;height:2px;background:#f0f4ff;border-radius:2px;transition:all 0.3s;}
.lj-nav-links{display:flex;align-items:center;gap:4px;list-style:none;margin:0;padding:0;}
.lj-nav-links > li > a{display:block;padding:8px 14px;color:#8a9bb5;text-decoration:none;font-size:14px;border-radius:8px;transition:all 0.2s;white-space:nowrap;}
.lj-nav-links > li > a:hover{color:#f0f4ff;background:rgba(0,87,184,0.15);}
.lj-nav-cta{background:linear-gradient(135deg,#0057b8,#00a8ff);color:#fff !important;padding:8px 18px !important;}
.lj-nav-cta:hover{box-shadow:0 4px 16px rgba(0,87,184,0.4);}
.lj-nav-lang{color:#00a8ff !important;font-weight:600;border:1px solid rgba(0,168,255,0.25);border-radius:20px !important;padding:6px 14px !important;}
.lj-nav-lang:hover{background:rgba(0,168,255,0.1) !important;}
.lj-dropdown{position:relative;}
.lj-dropdown-arrow{font-size:10px;margin-left:4px;}
.lj-dropdown-menu{display:none;position:absolute;top:100%;left:0;background:#0f1d35;border:1px solid rgba(0,87,184,0.25);border-radius:8px;min-width:160px;padding:6px;list-style:none;z-index:200;box-shadow:0 8px 32px rgba(0,0,0,0.4);}
.lj-dropdown:hover .lj-dropdown-menu{display:block;}
.lj-dropdown-menu li a{display:block;padding:8px 14px;color:#8a9bb5;text-decoration:none;font-size:13px;border-radius:6px;transition:all 0.2s;}
.lj-dropdown-menu li a:hover{color:#f0f4ff;background:rgba(0,87,184,0.15);}

/* ── 统一页脚 ── */
.lj-footer{background:linear-gradient(180deg,#0a1628,#050d1a);border-top:1px solid rgba(0,87,184,0.2);padding:40px 20px 20px;width:100%;}
.lj-footer-inner{max-width:1200px;margin:0 auto;}
.lj-footer-cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:30px;margin-bottom:30px;}
.lj-footer-col h4{font-size:14px;font-weight:700;color:#00a8ff;margin-bottom:14px;letter-spacing:1px;}
.lj-footer-col ul{list-style:none;padding:0;margin:0;}
.lj-footer-col ul li{margin-bottom:8px;}
.lj-footer-col ul li a{color:#8a9bb5;text-decoration:none;font-size:13px;transition:color 0.2s;}
.lj-footer-col ul li a:hover{color:#f0f4ff;}
.lj-footer-contact li{color:#8a9bb5;font-size:13px;line-height:1.8;}
.lj-footer-contact li a{color:#8a9bb5;text-decoration:none;}
.lj-footer-contact li a:hover{color:#00a8ff;}
.lj-footer-bottom{text-align:center;padding-top:20px;border-top:1px solid rgba(0,87,184,0.15);}
.lj-footer-bottom p{font-size:12px;color:#5a6d8a;line-height:1.8;margin:0;}
.lj-footer-tagline{font-size:11px;opacity:0.5;letter-spacing:1px;margin-top:4px !important;}

/* ── 浮动询盘栏 ── */
.lj-float-bar{position:fixed;bottom:0;left:0;right:0;z-index:1000;display:flex;background:rgba(10,22,40,0.97);backdrop-filter:blur(12px);border-top:1px solid rgba(0,87,184,0.25);padding:8px 12px;justify-content:space-around;align-items:center;}
.lj-float-item{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 12px;border-radius:8px;text-decoration:none;color:#8a9bb5;font-size:11px;transition:all 0.2s;cursor:pointer;background:none;border:none;font-family:inherit;}
.lj-float-item:active{transform:scale(0.95);}
.lj-float-phone{color:#00a8ff;}
.lj-float-wechat{color:#07c160;}
.lj-float-form{color:#f0f4ff;background:linear-gradient(135deg,#0057b8,#00a8ff);border-radius:8px;padding:6px 18px;}
.lj-float-form span{font-weight:600;font-size:12px;}

/* ── 桌面端浮动栏改为右下角气泡 ── */
@media(min-width:768px){
  .lj-float-bar{left:auto;right:24px;bottom:24px;flex-direction:column;gap:8px;background:rgba(10,22,40,0.9);border:1px solid rgba(0,87,184,0.25);border-radius:16px;padding:10px 8px;width:auto;box-shadow:0 8px 32px rgba(0,0,0,0.3);}
  .lj-float-item{padding:8px 10px;}
  .lj-float-form{padding:8px 16px;}
}

/* ── 手机导航响应式 ── */
@media(max-width:767px){
  .lj-nav-toggle{display:flex;}
  .lj-nav-links{display:none;position:absolute;top:56px;left:0;right:0;background:rgba(10,22,40,0.98);border-bottom:1px solid rgba(0,87,184,0.2);flex-direction:column;padding:8px 0;}
  .lj-nav-links.open{display:flex;}
  .lj-nav-links > li{width:100%;}
  .lj-nav-links > li > a{padding:12px 20px;border-radius:0;}
  .lj-dropdown-menu{position:static;display:none;background:rgba(0,0,0,0.2);border:none;border-radius:0;box-shadow:none;padding-left:20px;}
  .lj-dropdown.open .lj-dropdown-menu{display:block;}
  .lj-footer-cols{grid-template-columns:1fr;gap:20px;}
}

/* ── 页面内容留空（给浮动栏腾空间） ── */
body{padding-bottom:72px;}
@media(min-width:768px){body{padding-bottom:0;}}
"""

# ── 浮动微信复制脚本 ──────────────────────────────────────
FLOAT_SCRIPT = r"""
/* ── Language Toggle ── */
window.toggleLang = function(){
  var path = window.location.pathname;
  var newPath = path.startsWith('/en')
    ? path.replace(/^\/en(\/|$)/, '/')
    : '/en' + (path === '/' ? '/' : path);
  window.location.href = newPath;
};

/* ── 统一导航交互 ── */
(function(){
  'use strict';
  var toggle = document.getElementById('ljNavToggle');
  var links = document.getElementById('ljNavLinks');
  if(toggle && links){
    toggle.addEventListener('click', function(e){
      e.stopPropagation();
      links.classList.toggle('open');
    });
    document.addEventListener('click', function(e){
      if(!links.contains(e.target) && !toggle.contains(e.target)){
        links.classList.remove('open');
      }
    });
  }

  // 移动端下拉展开
  var dropdowns = document.querySelectorAll('.lj-dropdown');
  if(window.innerWidth <= 767){
    dropdowns.forEach(function(dd){
      dd.addEventListener('click', function(e){
        e.preventDefault();
        this.classList.toggle('open');
      });
    });
  }
})();

/* ── 浮动栏微信复制 ── */
window.copyWechatFloat = function(){
  var wechat = '""" + WECHAT + """';
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(wechat).then(function(){
      showFloatToast('微信号 ' + wechat + ' 已复制，打开微信添加');
    }).catch(function(){
      fallbackCopyFloat(wechat);
    });
  } else {
    fallbackCopyFloat(wechat);
  }
};
function fallbackCopyFloat(text){
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand('copy');
    showFloatToast('微信号 ' + text + ' 已复制');
  } catch(e) {
    showFloatToast('微信号: ' + text);
  }
  document.body.removeChild(ta);
}
function showFloatToast(msg){
  var t = document.getElementById('lj-toast');
  if(!t){
    t = document.createElement('div');
    t.id = 'lj-toast';
    t.style.cssText = 'position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:rgba(0,87,184,0.92);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999;opacity:0;transition:all 0.35s ease;pointer-events:none;backdrop-filter:blur(12px);border:1px solid rgba(0,168,255,0.2);white-space:nowrap;';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._hide);
  t._hide = setTimeout(function(){ t.style.opacity = '0'; }, 3000);
}
"""

# ── 注入函数 ──────────────────────────────────────────────

def inject_after_tag(html, tag, content):
    """在指定标签第一次出现后注入内容"""
    idx = html.find(tag)
    if idx == -1:
        return html
    idx_end = idx + len(tag)
    return html[:idx_end] + "\n" + content + html[idx_end:]


def inject_before_tag(html, tag, content):
    """在指定标签第一次出现前注入内容"""
    idx = html.find(tag)
    if idx == -1:
        return html
    return html[:idx] + content + "\n" + html[idx:]


def replace_between(html, start_marker, end_marker, new_content):
    """替换两个标记之间的内容（包含标记行本身）"""
    s = html.find(start_marker)
    if s == -1:
        return html
    e = html.find(end_marker, s + len(start_marker))
    if e == -1:
        return html
    e = e + len(end_marker)
    return html[:s] + new_content + html[e:]


def add_hreflang_tags(html, filename, is_en=False):
    """注入 hreflang + canonical + OG tags"""
    name_no_ext = filename.rsplit(".", 1)[0]
    zh_url = f"https://{DOMAIN}/products/{name_no_ext}.html"
    en_url = f"https://{DOMAIN}/en/products/{name_no_ext}.html"
    brand_name = BRAND_EN if is_en else BRAND_CN
    canonical = en_url if is_en else zh_url
    tags = f'  <link rel="canonical" href="{canonical}">\n'
    tags += f'  <link rel="alternate" hreflang="zh-CN" href="{zh_url}">\n'
    tags += f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
    tags += f'  <link rel="alternate" hreflang="x-default" href="{zh_url}">\n'
    tags += f'  <meta property="og:title" content="{name_no_ext} | {brand_name}">\n'
    tags += f'  <meta property="og:url" content="{canonical}">\n'
    tags += f'  <meta property="og:type" content="product">\n'
    tags += f'  <meta property="og:site_name" content="{brand_name}">\n'
    return inject_before_tag(html, "</head>", tags)


def patch_jsonld(html):
    """更新 JSON-LD 中的 url 字段"""
    # 找到 JSON-LD 块
    start = html.find('<script type="application/ld+json">')
    if start == -1:
        return html
    end = html.find("</script>", start)
    if end == -1:
        return html
    raw = html[start:end]
    
    try:
        # 提取 JSON
        json_start = raw.find(">") + 1
        json_str = raw[json_start:]
        data = json.loads(json_str)
        
        # 补充 url
        if "@type" in data and data["@type"] in ("Product", "Organization"):
            if "url" not in data:
                data["url"] = f"https://{DOMAIN}/"
            if "@type" == "Product" and "manufacturer" in data and isinstance(data["manufacturer"], dict):
                data["manufacturer"]["url"] = f"https://{DOMAIN}/"
            if "offers" in data and isinstance(data["offers"], dict):
                data["offers"]["url"] = f"https://{DOMAIN}/contact/"
        
        new_json = json.dumps(data, ensure_ascii=False, indent=2)
        new_raw = raw[:json_start] + new_json
        return html[:start] + new_raw + html[end:]
    except (json.JSONDecodeError, KeyError):
        return html


def patch_landing_file(filepath, is_en=False):
    """改造单个落地页（支持中/英文模式）"""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    filename = os.path.basename(filepath)
    original = html

    # 0. 更新 lang 属性
    if is_en:
        if 'lang="zh-CN"' in html:
            html = html.replace('lang="zh-CN"', 'lang="en"', 1)
        elif 'lang="' not in html[:200]:
            html = html.replace("<html", '<html lang="en"', 1)

    # 1. 注入 hreflang + canonical + OG
    html = add_hreflang_tags(html, filename, is_en)

    # 2. 更新 JSON-LD（复用旧函数）
    html = patch_jsonld(html)

    # 3. 注入导航栏
    html = inject_after_tag(html, "<body>", make_nav_html(is_en))

    # 4. 替换/注入页脚
    footer_html = make_footer_html(is_en)
    pattern = r'<footer\s+class="landing-footer">.*?</footer>'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, footer_html.strip(), html, count=1, flags=re.DOTALL)
    else:
        html = inject_after_tag(html, "</section>", footer_html)

    # 5. 注入浮动询盘栏
    html = inject_before_tag(html, "</body>", make_float_cta_html(is_en))

    # 6. 注入统一样式
    html = inject_before_tag(html, "</head>", f"<style>{NAV_STYLES}</style>\n")

    # 7. 注入交互脚本
    html = inject_before_tag(html, "</body>", f"<script>{FLOAT_SCRIPT}</script>\n")

    if html == original:
        print(f"  {filename} — 无变化, skip")
        return html

    if DRY_RUN:
        print(f"  {filename} — 可改造")
        return html

    return html


def main():
    global DRY_RUN
    mode = "zh"
    for a in sys.argv[1:]:
        if a == "--dry-run": DRY_RUN = True
        elif a == "--en": mode = "en"
        elif a == "--both": mode = "both"
        elif a == "--zh": mode = "zh"

    print(f"🔧 落地页双语改造工具")
    print(f"   目录: {LANDING_DIR}")
    print(f"   域名: {DOMAIN}")
    print(f"   语言: {mode}")
    print(f"   模式: {'🟡 预览' if DRY_RUN else '🔵 实际写入'}")
    print()

    if not os.path.isdir(LANDING_DIR):
        print(f"❌ 目录不存在: {LANDING_DIR}")
        return

    files = sorted([f for f in os.listdir(LANDING_DIR) if f.endswith(".html")])
    print(f"   找到 {len(files)} 个落地页")
    print()

    todo = []
    if mode in ("zh", "both"):
        todo.append((False, LANDING_DIR, "ZH"))
    if mode in ("en", "both"):
        todo.append((True, os.path.join(LANDING_DIR, "en"), "EN"))

    for is_en, out_dir, label in todo:
        if is_en:
            os.makedirs(out_dir, exist_ok=True)
        success = 0
        for fname in files:
            src = os.path.join(LANDING_DIR, fname)
            dst = os.path.join(out_dir, fname)
            if DRY_RUN:
                print(f"  [{label}] {fname} → {dst}")
                success += 1
                continue
            new_html = patch_landing_file(src, is_en=is_en)
            if new_html is not False and isinstance(new_html, str):
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(new_html)
                success += 1
        print(f"  [{label}] {success}/{len(files)} done → {out_dir}")
        print()

    print("✅ 全部完成")
    if not DRY_RUN and mode == "both":
        print("💡 部署建议:")
        print("   ZH: output/landing/*.html → /")
        print("   EN: output/landing/en/*.html → /en/")


if __name__ == "__main__":
    main()

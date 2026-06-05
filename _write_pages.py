import os
PAGES_DIR = r'D:\auto-video-platform\deploy'

COMMON_STYLE = r'''
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{--primary:#0057b8;--secondary:#00a8ff;--bg-dark:#0a1628;--bg-card:#0f1d35;--text-primary:#f0f4ff;--text-secondary:#8a9bb5;--text-muted:#5a6d8a;--border:rgba(0,87,184,0.25);--radius:12px;}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg-dark);color:var(--text-primary);line-height:1.6;overflow-x:hidden;}
.lj-nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(10,22,40,0.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);}
.lj-nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:0 20px;height:60px;}
.lj-nav-brand{display:flex;align-items:center;gap:8px;text-decoration:none;font-weight:700;font-size:18px;color:var(--text-primary);}
.lj-nav-dot{width:8px;height:8px;background:var(--secondary);border-radius:50%;box-shadow:0 0 12px var(--secondary);}
.lj-nav-links{display:flex;align-items:center;gap:6px;list-style:none;}
.lj-nav-links a{display:block;padding:8px 16px;color:var(--text-secondary);text-decoration:none;font-size:14px;border-radius:8px;transition:all 0.2s;}
.lj-nav-links a:hover{color:var(--text-primary);background:rgba(0,87,184,0.15);}
.lj-nav-cta{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff!important;}
.lj-nav-lang{color:#00a8ff!important;font-weight:600;border:1px solid rgba(0,168,255,0.25);border-radius:20px!important;padding:6px 14px!important;}
.lj-nav-toggle{display:none;background:none;border:none;cursor:pointer;padding:8px;flex-direction:column;gap:4px;}
.lj-nav-toggle span{display:block;width:22px;height:2px;background:#f0f4ff;border-radius:2px;transition:all 0.3s;}
.lj-dropdown{position:relative;}
.lj-dropdown-menu{display:none;position:absolute;top:100%;left:0;background:rgba(15,29,53,0.98);backdrop-filter:blur(12px);border:1px solid var(--border);border-radius:10px;padding:6px;min-width:180px;list-style:none;box-shadow:0 8px 32px rgba(0,0,0,0.4);z-index:200;}
.lj-dropdown-menu li a{display:block;padding:10px 16px;color:var(--text-secondary);text-decoration:none;font-size:13px;border-radius:6px;white-space:nowrap;}
.lj-dropdown-menu li a:hover{color:var(--text-primary);background:rgba(0,87,184,0.2);}
.lj-dropdown:hover .lj-dropdown-menu{display:block;}
.lj-footer{background:linear-gradient(180deg,#0a1628,#050d1a);border-top:1px solid var(--border);padding:40px 20px 20px;}
.lj-footer-inner{max-width:1200px;margin:0 auto;}
.lj-footer-cols{display:grid;grid-template-columns:1fr 1fr 1fr;gap:30px;margin-bottom:30px;}
.lj-footer-col h4{font-size:14px;font-weight:700;color:var(--secondary);margin-bottom:14px;letter-spacing:1px;}
.lj-footer-col ul{list-style:none;padding:0;}
.lj-footer-col ul li{margin-bottom:8px;}
.lj-footer-col ul li a{color:var(--text-secondary);text-decoration:none;font-size:13px;}
.lj-footer-contact li{color:var(--text-secondary);font-size:13px;line-height:1.8;}
.lj-footer-contact li a{color:var(--text-secondary);}
.lj-footer-bottom{text-align:center;padding-top:20px;border-top:1px solid var(--border);}
.lj-footer-bottom p{font-size:12px;color:var(--text-muted);}
.footer-wechat-qr{text-align:center;margin-top:8px;}
.footer-wechat-qr img{width:80px;height:80px;border-radius:8px;border:1px solid var(--border);padding:4px;cursor:pointer;background:var(--bg-card);}
.footer-wechat-qr .hint{font-size:10px;color:var(--text-muted);display:block;}
.lj-float-bar{position:fixed;bottom:0;left:0;right:0;z-index:1000;display:flex;background:rgba(10,22,40,0.97);backdrop-filter:blur(12px);border-top:1px solid var(--border);padding:8px 12px;justify-content:space-around;}
.lj-float-item{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 12px;border-radius:8px;text-decoration:none;color:var(--text-secondary);font-size:11px;background:none;border:none;cursor:pointer;font-family:inherit;}
.lj-float-phone{color:var(--secondary);}
.lj-float-wechat{color:#07c160;}
.lj-float-form{color:#fff;background:linear-gradient(135deg,var(--primary),var(--secondary));border-radius:8px;padding:6px 18px;}
body{padding-bottom:72px;}
.hero-btn{display:inline-flex;align-items:center;gap:8px;padding:14px 32px;border-radius:var(--radius);font-size:16px;font-weight:600;text-decoration:none;transition:all 0.25s;}
.hero-btn-primary{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;box-shadow:0 4px 24px rgba(0,87,184,0.35);}
.hero-btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,87,184,0.5);}
.hero-btn-secondary{background:rgba(255,255,255,0.06);color:var(--text-primary);border:1px solid rgba(255,255,255,0.12);}
@media(min-width:768px){.lj-float-bar{left:auto;right:24px;bottom:24px;flex-direction:column;gap:8px;background:rgba(10,22,40,0.9);border:1px solid var(--border);border-radius:16px;padding:10px 8px;width:auto;}body{padding-bottom:0;}}
@media(max-width:767px){.lj-nav-links{display:none;}.lj-footer-cols{grid-template-columns:1fr;}}
'''

MODAL_STYLE = '''
.lj-modal{display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px);align-items:center;justify-content:center;}
.lj-modal.show{display:flex;}
.lj-modal-content{background:var(--bg-card);border:1px solid var(--border);border-radius:16px;padding:32px;text-align:center;max-width:320px;position:relative;}
.lj-modal-content img{width:200px;height:200px;border-radius:12px;margin-bottom:12px;}
.lj-modal-content h3{font-size:18px;margin-bottom:4px;color:var(--text-primary);}
.lj-modal-content p{color:var(--text-secondary);font-size:13px;}
.lj-modal-close{position:absolute;top:8px;right:12px;background:none;border:none;color:var(--text-secondary);font-size:24px;cursor:pointer;line-height:1;}
'''

FOOTER_HTML = '''
<footer class="lj-footer">
  <div class="lj-footer-inner">
    <div class="lj-footer-cols">
      <div class="lj-footer-col">
        <h4>产品中心</h4>
        <ul>
          <li><a href="/products/?cat=绕线机">绕线机系列</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机系列</a></li>
          <li><a href="/products/?cat=插纸机">插纸机系列</a></li>
          <li><a href="/products/">全部设备</a></li>
        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>关于我们</h4>
        <ul>
          <li><a href="/about/">公司介绍</a></li>
          <li><a href="/cases/">客户案例</a></li>
        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>联系方式</h4>
        <ul class="lj-footer-contact">
          <li>\U0001f4de <a href="tel:18968693691">18968693691</a></li>
          <li>✉ 微信: ljzdh888</li>
          <li>\U0001f4cd 浙江台州椒江区刘洋工业园区</li>
        </ul>
        <div class="footer-wechat-qr">
          <img src="/assets/img/wechat-qr.jpg" alt="微信二维码" onclick="showWechatModal()">
          <span class="hint">\U0001f4f1 扫码添加微信</span>
        </div>
      </div>
    </div>
    <div class="lj-footer-bottom">
      <p>© 2026 台州隆江自动化设备有限公司 | 让绕线更智能</p>
    </div>
  </div>
</footer>'''

FLOAT_HTML = '''
<div class="lj-float-bar">
  <a class="lj-float-item lj-float-phone" href="tel:18968693691">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M6.62 10.79c1.44 2.83 3.76 5.15 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
    <span>电话咨询</span>
  </a>
  <button class="lj-float-item lj-float-wechat" onclick="copyWechatFloat()">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8.5 11C9.33 11 10 10.33 10 9.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm7 0c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zM12 2C6.48 2 2 6.48 2 12c0 1.88.54 3.63 1.48 5.11L2 22l4.92-1.48C8.36 21.46 10.12 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.54 0-3-.42-4.25-1.15l-.3-.18-2.92.87.88-2.85-.2-.32C4.42 15.35 4 13.78 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z"/></svg>
    <span>微信询价</span>
  </a>
  <a class="lj-float-item lj-float-form" href="/contact/">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM6 10h2v2H6zm0 4h8v2H6zm10 0h2v2h-2zm-6-4h8v2h-8z"/></svg>
    <span>获取方案</span>
  </a>
</div>'''

WECHAT_MODAL = '''
<div class="lj-modal" id="wechatModal" onclick="if(event.target===this)hideWechatModal()">
  <div class="lj-modal-content">
    <button class="lj-modal-close" onclick="hideWechatModal()">×</button>
    <img src="/assets/img/wechat-qr.jpg" alt="微信二维码">
    <h3>扫码添加微信</h3>
    <p>微信号: ljzdh888</p>
    <p style="font-size:11px;color:var(--text-muted);">请用真实二维码替换 /assets/img/wechat-qr.jpg</p>
  </div>
</div>'''

COMMON_SCRIPT = '''
<script>
window.toggleLang=function(){var p=window.location.pathname;window.location.href=p.startsWith("/en")?p.replace(/^\\/en(\\/|$)/,"/"):"/en"+(p==="/"?"/":p);};
document.addEventListener("DOMContentLoaded",function(){var t=document.getElementById("ljNavToggle"),l=document.getElementById("ljNavLinks");if(t&&l)t.addEventListener("click",function(){var o=l.style.display==="flex";l.style.display=o?"none":"flex";if(window.innerWidth<=767){l.style.flexDirection="column";l.style.position="absolute";l.style.top="60px";l.style.left="0";l.style.right="0";l.style.background="rgba(10,22,40,0.98)";l.style.borderBottom="1px solid var(--border)";l.style.padding="12px 20px";}});});
window.copyWechatFloat=function(){var w="ljzdh888",m="微信号 ljzdh888 已复制";if(navigator.clipboard)navigator.clipboard.writeText(w).then(function(){showFloatToast(m)}).catch(function(){fallbackCopy(w,m)});else fallbackCopy(w,m);};
function fallbackCopy(t,m){var a=document.createElement("textarea");a.value=t;a.style.position="fixed";a.style.left="-9999px";document.body.appendChild(a);a.select();try{document.execCommand("copy");showFloatToast(m)}catch(e){showFloatToast("微信号: ljzdh888")}document.body.removeChild(a);}
function showFloatToast(m){var t=document.getElementById("lj-toast");if(!t){t=document.createElement("div");t.id="lj-toast";t.style.cssText="position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:rgba(0,87,184,0.92);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999;opacity:0;transition:all 0.35s";document.body.appendChild(t);}t.textContent=m;t.style.opacity="1";clearTimeout(t._hide);t._hide=setTimeout(function(){t.style.opacity="0"},3000);}
window.showWechatModal=function(){var m=document.getElementById("wechatModal");if(m)m.classList.add("show");};
window.hideWechatModal=function(){var m=document.getElementById("wechatModal");if(m)m.classList.remove("show");};
</script>'''

def wp(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"OK: {path}")

print("Templates loaded")

# ===== ABOUT PAGE =====
about_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="台州隆江自动化设备有限公司 — 13年专注绕线机、磁钢机、插纸机研发制造，源头工厂直供">
<title>关于我们 — 台州隆江自动化设备有限公司</title>
<link rel="canonical" href="https://longjiang-ai.com/about/">
<style>""" + COMMON_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;max-width:600px;margin:0 auto;}
.section{padding:60px 20px;}
.section-inner{max-width:800px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.content-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:40px;}
.content-card p{color:var(--text-secondary);line-height:1.8;margin-bottom:16px;font-size:15px;}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-top:24px;}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;text-align:center;}
.stat-number{font-size:32px;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.stat-label{color:var(--text-secondary);font-size:14px;margin-top:4px;}
.cta-section{text-align:center;padding:60px 20px;}
.cta-section h2{font-size:24px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.cta-section p{color:var(--text-secondary);margin-bottom:24px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>台州隆江自动化</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/">首页</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">产品 ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/products/">全部产品</a></li>
          <li><a href="/products/?cat=绕线机">绕线机</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机</a></li>
          <li><a href="/products/?cat=插纸机">插纸机</a></li>
        </ul>
      </li>
      <li><a href=\"/videos/\">视频</a></li>
      <li><a href=\"/cases/\">案例</a></li>
      <li><a href=\"/about/\" style=\"color:var(--text-primary);background:rgba(0,87,184,0.15);\">关于</a></li>
      <li><a href=\"/contact/\" class=\"lj-nav-cta\">\U0001f4de 联系</a></li>
      <li><a href=\"javascript:toggleLang()\" class=\"lj-nav-lang\">\U0001f310 English</a></li>
    </ul>
  </div>
</nav>
<section class=\"page-hero\">
  <span class=\"section-label\">\U0001f3ed ABOUT</span>
  <h1>让绕线更智能</h1>
  <p>台州隆江自动化设备有限公司 — 绕线机 &amp; 自动化设备源头工厂</p>
</section>
<section class=\"section\">
  <div class=\"section-inner\">
    <div class=\"content-card\">
      <p>台州隆江自动化设备有限公司位于浙江省台州市椒江区，是一家集研发、设计、制造、销售与服务于一体的自动化设备制造企业。</p>
      <p>公司自2011年成立以来，始终专注于电机自动化设备的研发与制造。核心产品覆盖绕线机系列（内绕、外绕、飞叉、分块）、磁钢机系列（插磁钢、点胶、表贴）、插纸机系列等多个品类，共计37款设备，广泛应用于无刷电机、汽车电机、家用电器电机等领域。</p>
      <p>我们坚持\"让绕线更智能\"的理念，持续投入研发，拥有多项专利技术。所有设备均采用精密伺服控制与自动检测系统，确保产品一致性和良品率。作为源头工厂，我们提供从方案设计、设备制造到安装调试的一站式服务，支持非标定制，免费样机打样。</p>
      <p>隆江自动化期待与您携手，用智能装备提升您的生产效率。</p>
    </div>
    <div class=\"stats-grid\">
      <div class=\"stat-card\"><div class=\"stat-number\">13年+</div><div class=\"stat-label\">行业深耕</div></div>
      <div class=\"stat-card\"><div class=\"stat-number\">37款</div><div class=\"stat-label\">设备型号</div></div>
      <div class=\"stat-card\"><div class=\"stat-number\">100%</div><div class=\"stat-label\">源头工厂直供</div></div>
      <div class=\"stat-card\"><div class=\"stat-number\">√</div><div class=\"stat-label\">非标定制</div></div>
    </div>
  </div>
</section>
<section style=\"text-align:center;padding:60px 20px;\">
  <h2 style=\"font-size:24px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;\">需要定制设备方案？</h2>
  <p style=\"color:var(--text-secondary);margin-bottom:24px;\">联系我们获取专属方案 · 免费样机打样</p>
  <div>
    <a href=\"tel:18968693691\" class=\"hero-btn hero-btn-primary\">\U0001f4de 18968693691</a>
    <a href=\"/contact/\" class=\"hero-btn hero-btn-secondary\">✉ 在线咨询</a>
  </div>
</section>
""" + FOOTER_HTML + FLOAT_HTML + WECHAT_MODAL + COMMON_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'about', 'index.html'), about_html)
print("About page written")

# ===== CONTACT PAGE =====
contact_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="联系台州隆江自动化设备有限公司 — 电话18968693691，微信ljzdh888，获取绕线机报价">
<title>联系我们 — 台州隆江自动化设备有限公司</title>
<link rel="canonical" href="https://longjiang-ai.com/contact/">
<style>""" + COMMON_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:700px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.contact-grid{display:grid;gap:20px;}
.contact-item{display:flex;align-items:center;gap:16px;padding:20px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);transition:all 0.3s;}
.contact-item:hover{border-color:var(--secondary);transform:translateY(-2px);}
.contact-icon{font-size:28px;width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:rgba(0,87,184,0.1);border-radius:12px;}
.contact-info h3{font-size:15px;font-weight:700;margin-bottom:4px;}
.contact-info .val{color:var(--secondary);font-size:17px;font-weight:600;text-decoration:none;display:block;}
.contact-info .val a{color:var(--secondary);text-decoration:none;}
.contact-info .desc{color:var(--text-muted);font-size:12px;margin-top:2px;}
.cta-wrap{text-align:center;margin-top:32px;}
.map-placeholder{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:60px 20px;text-align:center;margin-top:24px;}
.map-placeholder .icon{font-size:48px;opacity:0.3;}
.map-placeholder p{color:var(--text-muted);font-size:13px;margin-top:8px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>台州隆江自动化</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/">首页</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">产品 ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/products/">全部产品</a></li>
          <li><a href="/products/?cat=绕线机">绕线机</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机</a></li>
          <li><a href="/products/?cat=插纸机">插纸机</a></li>
        </ul>
      </li>
      <li><a href="/videos/">视频</a></li>
      <li><a href="/cases/">案例</a></li>
      <li><a href="/about/">关于</a></li>
      <li><a href="/contact/" class="lj-nav-cta">\U0001f4de 联系</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 English</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">\U0001f4de CONTACT</span>
  <h1>联系我们</h1>
  <p>随时为您提供自动化设备咨询与报价</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="contact-grid">
      <div class="contact-item">
        <div class="contact-icon">\U0001f4de</div>
        <div class="contact-info">
          <h3>电话</h3>
          <div class="val"><a href="tel:18968693691">18968693691</a></div>
          <div class="desc">工作日 8:00-18:00 在线</div>
        </div>
      </div>
      <div class="contact-item" onclick="showWechatModal()" style="cursor:pointer;">
        <div class="contact-icon">\U0001f4ac</div>
        <div class="contact-info">
          <h3>微信</h3>
          <div class="val">ljzdh888</div>
          <div class="desc">点击查看二维码 →</div>
        </div>
      </div>
      <div class="contact-item">
        <div class="contact-icon">\U0001f4cd</div>
        <div class="contact-info">
          <h3>地址</h3>
          <div class="val" style="font-size:15px;color:var(--text-primary);">浙江台州椒江区刘洋工业园区</div>
          <div class="desc">欢迎来访参观、打样测试</div>
        </div>
      </div>
      <div class="contact-item">
        <div class="contact-icon">✉</div>
        <div class="contact-info">
          <h3>邮箱 / QQ</h3>
          <div class="val" style="font-size:15px;color:var(--text-primary);">请致电索取</div>
          <div class="desc">或添加微信获取详细联系方式</div>
        </div>
      </div>
    </div>
    <div class="cta-wrap">
      <a href="tel:18968693691" class="hero-btn hero-btn-primary" style="font-size:18px;padding:16px 40px;">\U0001f4de 立即拨打 18968693691</a>
    </div>
    <div class="map-placeholder">
      <div class="icon">\U0001f5fa</div>
      <p>地图区域 — 浙江台州椒江区刘洋工业园区</p>
      <p style="font-size:11px;margin-top:4px;">请在真实部署时嵌入百度/高德地图</p>
    </div>
  </div>
</section>
""" + FOOTER_HTML + FLOAT_HTML + WECHAT_MODAL + COMMON_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'contact', 'index.html'), contact_html)
print("Contact page written")

# ===== CASES PAGE =====
cases_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="台州隆江自动化设备客户案例 — 绕线机、磁钢机在各行业的应用">
<title>客户案例 — 台州隆江自动化设备有限公司</title>
<link rel="canonical" href="https://longjiang-ai.com/cases/">
<style>""" + COMMON_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:900px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;}
.case-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:all 0.3s;}
.case-card:hover{border-color:var(--secondary);transform:translateY(-3px);}
.case-img{width:100%;height:160px;background:linear-gradient(135deg,rgba(0,87,184,0.08),rgba(0,168,255,0.04));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:48px;color:var(--border);margin-bottom:16px;}
.case-card h3{font-size:17px;font-weight:700;margin-bottom:6px;}
.case-card .industry{color:var(--secondary);font-size:12px;margin-bottom:8px;display:block;}
.case-card p{color:var(--text-secondary);font-size:13px;line-height:1.6;}
.cta-card{background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);padding:60px 20px;text-align:center;margin-top:32px;}
.cta-card .big-icon{font-size:64px;margin-bottom:16px;opacity:0.4;}
.cta-card h3{font-size:20px;margin-bottom:8px;}
.cta-card p{color:var(--text-secondary);margin-bottom:20px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>台州隆江自动化</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/">首页</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">产品 ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/products/">全部产品</a></li>
          <li><a href="/products/?cat=绕线机">绕线机</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机</a></li>
          <li><a href="/products/?cat=插纸机">插纸机</a></li>
        </ul>
      </li>
      <li><a href="/videos/">视频</a></li>
      <li><a href="/cases/" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">案例</a></li>
      <li><a href="/about/">关于</a></li>
      <li><a href="/contact/" class="lj-nav-cta">\U0001f4de 联系</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 English</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">⭐ CASES</span>
  <h1>客户案例</h1>
  <p>让每台设备在客户现场发挥价值</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="cases-grid">
      <div class="case-card">
        <div class="case-img">\U0001f3ed</div>
        <h3>某无刷电机厂家</h3>
        <span class="industry">绕线机 · 200台/天 → 350台/天</span>
        <p>采用LJ-7HS双工位绕线机替代旧设备，生产效率提升75%，良品率从92%提升至98.5%。</p>
      </div>
      <div class="case-card">
        <div class="case-img">\U0001f4e1</div>
        <h3>某家电零部件企业</h3>
        <span class="industry">磁钢机 · 自动化升级</span>
        <p>引入全自动插磁钢点胶一体机，取消人工点胶工序，每班节省4名人工，年节省人工成本约40万。</p>
      </div>
      <div class="case-card">
        <div class="case-img">\U0001f697</div>
        <h3>某汽车电机供应商</h3>
        <span class="industry">综合设备方案 · 全流程</span>
        <p>采用隆江绕线机+磁钢机+检测设备全套方案，实现电机定子生产全自动化，产线节奏12秒/件。</p>
      </div>
    </div>
    <div class="cta-card">
      <div class="big-icon">\U0001f3c6</div>
      <h3>案例内容持续更新中</h3>
      <p>我们的设备已服务于多家电机、家电及汽车零部件企业。如需了解同行应用情况，请联系我们获取详情。</p>
      <a href="/contact/" class="hero-btn hero-btn-primary">\U0001f4de 咨询案例详情</a>
    </div>
  </div>
</section>
""" + FOOTER_HTML + FLOAT_HTML + WECHAT_MODAL + COMMON_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'cases', 'index.html'), cases_html)
print("Cases page written")

# ===== PRODUCTS PAGE =====
products_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="台州隆江自动化设备产品列表 — 37款绕线机、磁钢机、插纸机，源头工厂直供">
<title>产品中心 — 台州隆江自动化设备有限公司</title>
<link rel="canonical" href="https://longjiang-ai.com/products/">
<style>""" + COMMON_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:1200px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.cat-tabs{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;}
.cat-tab{padding:8px 20px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--text-secondary);font-size:13px;cursor:pointer;transition:all 0.2s;text-decoration:none;}
.cat-tab:hover{color:var(--text-primary);background:rgba(0,87,184,0.1);}
.cat-tab.active{background:linear-gradient(135deg,var(--primary),var(--secondary));border-color:transparent;color:#fff;}
.products-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;}
.product-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-decoration:none;transition:all 0.3s;display:flex;flex-direction:column;}
.product-card:hover{transform:translateY(-3px);border-color:var(--secondary);box-shadow:0 8px 24px rgba(0,87,184,0.12);}
.product-card .p-img{width:100%;height:140px;background:linear-gradient(135deg,rgba(0,87,184,0.1),rgba(0,168,255,0.05));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:36px;color:var(--border);margin-bottom:12px;}
.product-card h3{font-size:15px;font-weight:700;color:var(--text-primary);margin-bottom:4px;}
.product-card .model{font-size:12px;color:var(--text-muted);margin-bottom:6px;}
.product-card .desc{font-size:13px;color:var(--text-secondary);line-height:1.5;flex:1;}
.product-card .tag{display:inline-block;padding:2px 10px;background:rgba(0,87,184,0.12);border-radius:12px;font-size:11px;color:var(--secondary);align-self:flex-start;margin-top:8px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}.products-grid{grid-template-columns:repeat(2,1fr);}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>台州隆江自动化</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/">首页</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">产品 ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/products/">全部产品</a></li>
          <li><a href="/products/?cat=绕线机">绕线机</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机</a></li>
          <li><a href="/products/?cat=插纸机">插纸机</a></li>
        </ul>
      </li>
      <li><a href="/videos/">视频</a></li>
      <li><a href="/cases/">案例</a></li>
      <li><a href="/about/">关于</a></li>
      <li><a href="/contact/" class="lj-nav-cta">\U0001f4de 联系</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 English</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">⚙ PRODUCTS</span>
  <h1>产品中心</h1>
  <p>37款设备覆盖绕线、装配、检测全工序</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="cat-tabs">
      <a href="/products/" class="cat-tab active">全部</a>
      <a href="/products/?cat=绕线机" class="cat-tab">绕线机 (19)</a>
      <a href="/products/?cat=磁钢机" class="cat-tab">磁钢机 (16)</a>
      <a href="/products/?cat=插纸机" class="cat-tab">插纸机 (2)</a>
      <a href="/products/?cat=其他" class="cat-tab">其他 (2)</a>
    </div>
    <div class="products-grid">
      <a href="/products/LJ-7HS-3%E5%8F%8C%E5%B7%A5%E4%BD%8D%E7%BB%95%E7%BA%BF%E6%9C%BA.html" class="product-card">
        <div class="p-img">⚙</div>
        <h3>LJ-7HS-3 双工位绕线机</h3>
        <div class="model">双工位 · 高速内绕</div>
        <div class="desc">适合无刷电机定子绕线，生产效率提升30%</div>
        <span class="tag">绕线机</span>
      </a>
      <a href="/products/18%E5%86%85%E6%8F%92%E8%A3%85%E7%A3%81%E9%92%A2%E6%9C%BA.html" class="product-card">
        <div class="p-img">\U0001f9f2</div>
        <h3>18内插装磁钢机</h3>
        <div class="model">内转子 · 自动插磁钢</div>
        <div class="desc">适配18mm内转子磁钢自动装配</div>
        <span class="tag">磁钢机</span>
      </a>
      <a href="/products/%E9%AB%98%E9%80%9F%E5%9B%9B%E5%B7%A5%E4%BD%8D%E7%BB%95%E7%BA%BF%E6%9C%BA.html" class="product-card">
        <div class="p-img">⚙</div>
        <h3>高速四工位绕线机</h3>
        <div class="model">四工位 · 高效率</div>
        <div class="desc">四工位同时绕线，大批量生产首选</div>
        <span class="tag">绕线机</span>
      </a>
      <a href="/products/LJ-CZJ-Y01.html" class="product-card">
        <div class="p-img">\U0001f4c4</div>
        <h3>LJ-CZJ-Y01 插纸机</h3>
        <div class="model">自动插纸</div>
        <div class="desc">定子槽纸自动插装</div>
        <span class="tag">插纸机</span>
      </a>
    </div>
    <div style="text-align:center;margin-top:40px;padding:40px;background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);">
      <p style="color:var(--text-secondary);margin-bottom:16px;">以上仅为部分展示，全系列37款设备尽在官网</p>
      <a href="tel:18968693691" class="hero-btn hero-btn-primary">\U0001f4de 咨询全部产品</a>
      <p style="color:var(--text-muted);font-size:12px;margin-top:12px;">产品页面图片占位 — 请替换为实际设备照片</p>
    </div>
  </div>
</section>
""" + FOOTER_HTML + FLOAT_HTML + WECHAT_MODAL + COMMON_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'products', 'index.html'), products_html)
print("Products page written")

# ===== VIDEOS PAGE =====
videos_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="台州隆江自动化设备视频展示 — 绕线机、磁钢机运行演示">
<title>视频展示 — 台州隆江自动化设备有限公司</title>
<link rel="canonical" href="https://longjiang-ai.com/videos/">
<style>""" + COMMON_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:1000px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.videos-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;}
.video-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;transition:all 0.3s;}
.video-card:hover{border-color:var(--secondary);transform:translateY(-3px);}
.video-thumb{width:100%;height:180px;background:linear-gradient(135deg,rgba(0,87,184,0.12),rgba(0,168,255,0.06));display:flex;align-items:center;justify-content:center;font-size:48px;color:var(--border);position:relative;}
.video-thumb .play-btn{position:absolute;width:56px;height:56px;border-radius:50%;background:rgba(0,87,184,0.8);display:flex;align-items:center;justify-content:center;font-size:22px;color:#fff;}
.video-card:hover .play-btn{background:rgba(0,87,184,1);transform:scale(1.1);}
.video-info{padding:16px;}
.video-info h3{font-size:15px;font-weight:700;margin-bottom:4px;}
.video-info p{font-size:13px;color:var(--text-secondary);}
.placeholder-notice{text-align:center;padding:80px 20px;background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);margin-top:24px;}
.placeholder-notice .icon{font-size:64px;opacity:0.3;margin-bottom:16px;}
.placeholder-notice h3{font-size:18px;margin-bottom:8px;}
.placeholder-notice p{color:var(--text-secondary);font-size:14px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>台州隆江自动化</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/">首页</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">产品 ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/products/">全部产品</a></li>
          <li><a href="/products/?cat=绕线机">绕线机</a></li>
          <li><a href="/products/?cat=磁钢机">磁钢机</a></li>
          <li><a href="/products/?cat=插纸机">插纸机</a></li>
        </ul>
      </li>
      <li><a href="/videos/" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">视频</a></li>
      <li><a href="/cases/">案例</a></li>
      <li><a href="/about/">关于</a></li>
      <li><a href="/contact/" class="lj-nav-cta">\U0001f4de 联系</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 English</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">\U0001f3ac VIDEOS</span>
  <h1>视频展示</h1>
  <p>直观看到设备运行实景</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="videos-grid">
      <div class="video-card">
        <div class="video-thumb">⚙<div class="play-btn">▶</div></div>
        <div class="video-info"><h3>双工位绕线机运行实景</h3><p>LJ-7HS-3 高速绕线演示</p></div>
      </div>
      <div class="video-card">
        <div class="video-thumb">\U0001f9f2<div class="play-btn">▶</div></div>
        <div class="video-info"><h3>自动插磁钢机工作原理</h3><p>内插装磁钢机实机演示</p></div>
      </div>
      <div class="video-card">
        <div class="video-thumb">\U0001f4c4<div class="play-btn">▶</div></div>
        <div class="video-info"><h3>插纸机自动化流程</h3><p>定子槽纸自动插装演示</p></div>
      </div>
    </div>
    <div class="placeholder-notice">
      <div class="icon">\U0001f3ac</div>
      <h3>更多视频持续上传中</h3>
      <p>当前为图片占位状态，请将视频文件放入 deploy/videos/ 目录</p>
      <p style="font-size:12px;margin-top:8px;color:var(--text-muted);">支持 mp4 / webm 格式，建议比例 16:9</p>
    </div>
  </div>
</section>
""" + FOOTER_HTML + FLOAT_HTML + WECHAT_MODAL + COMMON_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'videos', 'index.html'), videos_html)
print("Videos page written")

# ===== ENGLISH PAGES =====
EN_STYLE = COMMON_STYLE.replace('font-family:-apple-system,BlinkMacSystemFont,"Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;','font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;')

EN_FOOTER = '''
<footer class="lj-footer">
  <div class="lj-footer-inner">
    <div class="lj-footer-cols">
      <div class="lj-footer-col">
        <h4>Products</h4>
        <ul>
          <li><a href="/products/?cat=Winding Machine">Winding Machine</a></li>
          <li><a href="/products/?cat=Magnet Machine">Magnet Machine</a></li>
          <li><a href="/products/?cat=Paper Inserter">Paper Inserter</a></li>
          <li><a href="/products/">All Products</a></li>
        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>About Us</h4>
        <ul>
          <li><a href="/en/about/">Company</a></li>
          <li><a href="/en/cases/">Case Studies</a></li>
        </ul>
      </div>
      <div class="lj-footer-col">
        <h4>Contact</h4>
        <ul class="lj-footer-contact">
          <li>\U0001f4de <a href="tel:18968693691">18968693691</a></li>
          <li>✉ WeChat: ljzdh888</li>
          <li>\U0001f4cd Jiaojiang, Taizhou, Zhejiang</li>
        </ul>
        <div class="footer-wechat-qr">
          <img src="/assets/img/wechat-qr.jpg" alt="WeChat QR" onclick="showWechatModal()">
          <span class="hint">\U0001f4f1 Scan to add WeChat</span>
        </div>
      </div>
    </div>
    <div class="lj-footer-bottom">
      <p>© 2026 Taizhou Longjiang Automation Equipment Co., Ltd.</p>
    </div>
  </div>
</footer>'''

EN_FLOAT = FLOAT_HTML.replace('电话咨询', 'Call Us').replace('微信询价', 'WeChat').replace('获取方案', 'Get Quote')

EN_SCRIPT = COMMON_SCRIPT.replace('toggleLang', 'toggleLang')
# Keep toggleLang as is since it switches /en <-> /

en_about = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Taizhou Longjiang Automation - 13 years of winding machine, magnet machine, paper inserter manufacturing">
<title>About - Taizhou Longjiang Automation Equipment Co., Ltd.</title>
<link rel="canonical" href="https://longjiang-ai.com/en/about/">
<style>""" + EN_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;max-width:600px;margin:0 auto;}
.section{padding:60px 20px;}
.section-inner{max-width:800px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.content-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:40px;}
.content-card p{color:var(--text-secondary);line-height:1.8;margin-bottom:16px;font-size:15px;}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-top:24px;}
.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;text-align:center;}
.stat-number{font-size:32px;font-weight:800;background:linear-gradient(135deg,var(--primary),var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.stat-label{color:var(--text-secondary);font-size:14px;margin-top:4px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>Longjiang Automation</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/en/">Home</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">Products ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/en/products/">All Products</a></li>
          <li><a href="/en/products/?cat=Winding+Machine">Winding Machine</a></li>
          <li><a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a></li>
          <li><a href="/en/products/?cat=Paper+Inserter">Paper Inserter</a></li>
        </ul>
      </li>
      <li><a href="/en/videos/">Videos</a></li>
      <li><a href="/en/cases/">Cases</a></li>
      <li><a href="/en/about/" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">About</a></li>
      <li><a href="/en/contact/" class="lj-nav-cta">\U0001f4de Contact</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 中文</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">\U0001f3ed ABOUT</span>
  <h1>Smarter Winding Solutions</h1>
  <p>Taizhou Longjiang Automation — Factory-Direct Automation Equipment Manufacturer</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="content-card">
      <p>Taizhou Longjiang Automation Equipment Co., Ltd. is located in Jiaojiang District, Taizhou City, Zhejiang Province. We are an enterprise integrating R&D, design, manufacturing, sales and service of automation equipment.</p>
      <p>Since 2011, we have focused on motor automation equipment. Our core products cover Winding Machines (inner winding, outer winding, flyer, segmented), Magnet Machines (insertion, dispensing, surface mount), Paper Inserters and more — 37 models in total, widely used in brushless motors, automotive motors, and home appliance motors.</p>
      <p>We adhere to the concept of "Smarter Winding Solutions", continuously investing in R&D with multiple patented technologies. All equipment uses precision servo control and automatic inspection systems. As a factory-direct manufacturer, we provide one-stop service from design to installation, supporting custom non-standard solutions with free sample testing.</p>
    </div>
    <div class="stats-grid">
      <div class="stat-card"><div class="stat-number">13+</div><div class="stat-label">Years Experience</div></div>
      <div class="stat-card"><div class="stat-number">37</div><div class="stat-label">Equipment Models</div></div>
      <div class="stat-card"><div class="stat-number">100%</div><div class="stat-label">Factory Direct</div></div>
      <div class="stat-card"><div class="stat-number">✓</div><div class="stat-label">Custom Solutions</div></div>
    </div>
  </div>
</section>
<section style="text-align:center;padding:60px 20px;">
  <h2 style="font-size:24px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Need a Custom Solution?</h2>
  <p style="color:var(--text-secondary);margin-bottom:24px;">Contact us for a quote · Free sample testing</p>
  <div>
    <a href="tel:18968693691" class="hero-btn hero-btn-primary">\U0001f4de +86 18968693691</a>
    <a href="/en/contact/" class="hero-btn hero-btn-secondary">✉ Inquiry</a>
  </div>
</section>
""" + EN_FOOTER + EN_FLOAT + WECHAT_MODAL + EN_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'en', 'about', 'index.html'), en_about)
print("EN about written")

en_contact = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Contact Taizhou Longjiang Automation - Tel: 18968693691, WeChat: ljzdh888">
<title>Contact - Taizhou Longjiang Automation</title>
<link rel="canonical" href="https://longjiang-ai.com/en/contact/">
<style>""" + EN_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:700px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.contact-grid{display:grid;gap:20px;}
.contact-item{display:flex;align-items:center;gap:16px;padding:20px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);}
.contact-item:hover{border-color:var(--secondary);}
.contact-icon{font-size:28px;width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:rgba(0,87,184,0.1);border-radius:12px;}
.contact-info h3{font-size:15px;font-weight:700;margin-bottom:4px;}
.contact-info .val{color:var(--secondary);font-size:17px;font-weight:600;}
.contact-info .val a{color:var(--secondary);text-decoration:none;}
.contact-info .desc{color:var(--text-muted);font-size:12px;margin-top:2px;}
.cta-wrap{text-align:center;margin-top:32px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>Longjiang Automation</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/en/">Home</a></li>
      <li class="lj-dropdown">
        <a href="javascript:void(0)">Products ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/en/products/">All Products</a></li>
          <li><a href="/en/products/?cat=Winding+Machine">Winding Machine</a></li>
          <li><a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a></li>
        </ul>
      </li>
      <li><a href="/en/videos/">Videos</a></li>
      <li><a href="/en/cases/">Cases</a></li>
      <li><a href="/en/about/">About</a></li>
      <li><a href="/en/contact/" class="lj-nav-cta">\U0001f4de Contact</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 中文</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">\U0001f4de CONTACT</span>
  <h1>Get In Touch</h1>
  <p>We are here to help with your automation needs</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="contact-grid">
      <div class="contact-item">
        <div class="contact-icon">\U0001f4de</div>
        <div class="contact-info"><h3>Phone</h3><div class="val"><a href="tel:18968693691">+86 18968693691</a></div><div class="desc">Mon-Sat 8:00-18:00 CST</div></div>
      </div>
      <div class="contact-item" onclick="showWechatModal()" style="cursor:pointer;">
        <div class="contact-icon">\U0001f4ac</div>
        <div class="contact-info"><h3>WeChat</h3><div class="val">ljzdh888</div><div class="desc">Click to view QR code</div></div>
      </div>
      <div class="contact-item">
        <div class="contact-icon">\U0001f4cd</div>
        <div class="contact-info"><h3>Address</h3><div class="val" style="font-size:15px;color:var(--text-primary);">Jiaojiang, Taizhou, Zhejiang, China</div><div class="desc">Factory visits welcome</div></div>
      </div>
    </div>
    <div class="cta-wrap">
      <a href="tel:18968693691" class="hero-btn hero-btn-primary" style="font-size:18px;padding:16px 40px;">\U0001f4de Call +86 18968693691</a>
      <a href="https://wa.me/8618968693691" class="hero-btn hero-btn-secondary" style="margin-left:12px;" target="_blank">\U0001f4ac WhatsApp</a>
    </div>
  </div>
</section>
""" + EN_FOOTER + EN_FLOAT + WECHAT_MODAL + EN_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'en', 'contact', 'index.html'), en_contact)
print("EN contact written")

en_cases = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Longjiang Automation customer cases - winding machines, magnet machines in action">
<title>Case Studies - Longjiang Automation</title>
<link rel="canonical" href="https://longjiang-ai.com/en/cases/">
<style>""" + EN_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:900px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.cases-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;}
.case-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;transition:all 0.3s;}
.case-card:hover{border-color:var(--secondary);transform:translateY(-3px);}
.case-img{width:100%;height:160px;background:linear-gradient(135deg,rgba(0,87,184,0.08),rgba(0,168,255,0.04));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:48px;color:var(--border);margin-bottom:16px;}
.case-card h3{font-size:17px;font-weight:700;margin-bottom:6px;}
.case-card .industry{color:var(--secondary);font-size:12px;margin-bottom:8px;display:block;}
.case-card p{color:var(--text-secondary);font-size:13px;line-height:1.6;}
.cta-card{background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);padding:60px 20px;text-align:center;margin-top:32px;}
.cta-card .big-icon{font-size:64px;margin-bottom:16px;opacity:0.4;}
.cta-card h3{font-size:20px;margin-bottom:8px;}
.cta-card p{color:var(--text-secondary);margin-bottom:20px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>Longjiang Automation</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/en/">Home</a></li>
      <li class="lj-dropdown"><a href="javascript:void(0)">Products ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/en/products/">All Products</a></li>
          <li><a href="/en/products/?cat=Winding+Machine">Winding Machine</a></li>
          <li><a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a></li>
        </ul>
      </li>
      <li><a href="/en/videos/">Videos</a></li>
      <li><a href="/en/cases/" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">Cases</a></li>
      <li><a href="/en/about/">About</a></li>
      <li><a href="/en/contact/" class="lj-nav-cta">\U0001f4de Contact</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 中文</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">⭐ CASES</span>
  <h1>Customer Stories</h1>
  <p>Real results from real deployments</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="cases-grid">
      <div class="case-card">
        <div class="case-img">\U0001f3ed</div>
        <h3>Brushless Motor Manufacturer</h3>
        <span class="industry">Winding Machine · 200 → 350 units/day</span>
        <p>Switched to LJ-7HS dual-spindle winding machine. Production efficiency up 75%, yield from 92% to 98.5%.</p>
      </div>
      <div class="case-card">
        <div class="case-img">\U0001f4e1</div>
        <h3>Home Appliance Parts Supplier</h3>
        <span class="industry">Magnet Machine · Automation Upgrade</span>
        <p>Automated magnet insertion and dispensing, eliminated 4 manual positions per shift, saving ~$55K/year.</p>
      </div>
      <div class="case-card">
        <div class="case-img">\U0001f697</div>
        <h3>Automotive Motor Supplier</h3>
        <span class="industry">Full Line Solution</span>
        <p>Complete winding + magnet + inspection line. Fully automated stator production at 12 sec/part cycle time.</p>
      </div>
    </div>
    <div class="cta-card">
      <div class="big-icon">\U0001f3c6</div>
      <h3>More Case Studies Coming</h3>
      <p>Our equipment serves motor, appliance and automotive manufacturers. Contact us for details.</p>
      <a href="/en/contact/" class="hero-btn hero-btn-primary">\U0001f4de Inquire</a>
    </div>
  </div>
</section>
""" + EN_FOOTER + EN_FLOAT + WECHAT_MODAL + EN_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'en', 'cases', 'index.html'), en_cases)
print("EN cases written")

en_videos = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Longjiang Automation equipment videos - winding machines, magnet machines in action">
<title>Videos - Longjiang Automation</title>
<link rel="canonical" href="https://longjiang-ai.com/en/videos/">
<style>""" + EN_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:1000px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.videos-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;}
.video-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;transition:all 0.3s;}
.video-card:hover{border-color:var(--secondary);transform:translateY(-3px);}
.video-thumb{width:100%;height:180px;background:linear-gradient(135deg,rgba(0,87,184,0.12),rgba(0,168,255,0.06));display:flex;align-items:center;justify-content:center;font-size:48px;color:var(--border);position:relative;}
.video-thumb .play-btn{position:absolute;width:56px;height:56px;border-radius:50%;background:rgba(0,87,184,0.8);display:flex;align-items:center;justify-content:center;font-size:22px;color:#fff;}
.video-card:hover .play-btn{background:rgba(0,87,184,1);transform:scale(1.1);}
.video-info{padding:16px;}
.video-info h3{font-size:15px;font-weight:700;margin-bottom:4px;}
.video-info p{font-size:13px;color:var(--text-secondary);}
.placeholder-notice{text-align:center;padding:80px 20px;background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);margin-top:24px;}
.placeholder-notice .icon{font-size:64px;opacity:0.3;margin-bottom:16px;}
.placeholder-notice h3{font-size:18px;margin-bottom:8px;}
.placeholder-notice p{color:var(--text-secondary);font-size:14px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>Longjiang Automation</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/en/">Home</a></li>
      <li class="lj-dropdown"><a href="javascript:void(0)">Products ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/en/products/">All Products</a></li>
          <li><a href="/en/products/?cat=Winding+Machine">Winding Machine</a></li>
          <li><a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a></li>
        </ul>
      </li>
      <li><a href="/en/videos/" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">Videos</a></li>
      <li><a href="/en/cases/">Cases</a></li>
      <li><a href="/en/about/">About</a></li>
      <li><a href="/en/contact/" class="lj-nav-cta">\U0001f4de Contact</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 中文</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">\U0001f3ac VIDEOS</span>
  <h1>Equipment in Action</h1>
  <p>See our machines running in real production</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="videos-grid">
      <div class="video-card"><div class="video-thumb">⚙<div class="play-btn">▶</div></div><div class="video-info"><h3>Dual-spindle Winding Machine</h3><p>LJ-7HS-3 high-speed winding demo</p></div></div>
      <div class="video-card"><div class="video-thumb">\U0001f9f2<div class="play-btn">▶</div></div><div class="video-info"><h3>Magnet Insertion Machine</h3><p>Automatic magnet assembly demo</p></div></div>
      <div class="video-card"><div class="video-thumb">\U0001f4c4<div class="play-btn">▶</div></div><div class="video-info"><h3>Paper Inserter in Action</h3><p>Automatic slot paper insertion</p></div></div>
    </div>
    <div class="placeholder-notice">
      <div class="icon">\U0001f3ac</div>
      <h3>More Videos Uploading</h3>
      <p>Current placeholders — replace with actual video files in deploy/videos/</p>
      <p style="font-size:12px;margin-top:8px;color:var(--text-muted);">Supports mp4 / webm, 16:9 recommended</p>
    </div>
  </div>
</section>
""" + EN_FOOTER + EN_FLOAT + WECHAT_MODAL + EN_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'en', 'videos', 'index.html'), en_videos)
print("EN videos written")

en_products = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="Longjiang Automation products - winding machines, magnet machines, paper inserters">
<title>Products - Longjiang Automation</title>
<link rel="canonical" href="https://longjiang-ai.com/en/products/">
<style>""" + EN_STYLE + MODAL_STYLE + """
.page-hero{padding:100px 20px 40px;background:linear-gradient(135deg,#0a1628,#1a2a4a);text-align:center;position:relative;overflow:hidden;}
.page-hero::before{content:'';position:absolute;top:-50%;right:-30%;width:600px;height:600px;background:radial-gradient(circle,rgba(0,87,184,0.12),transparent 70%);}
.page-hero>*{position:relative;z-index:2;}
.page-hero h1{font-size:36px;font-weight:800;margin-bottom:12px;background:linear-gradient(135deg,#fff,var(--secondary));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.page-hero p{color:var(--text-secondary);font-size:16px;}
.section{padding:60px 20px;}
.section-inner{max-width:1200px;margin:0 auto;}
.section-label{display:inline-block;padding:6px 16px;background:rgba(0,87,184,0.1);border-radius:20px;font-size:12px;color:var(--secondary);letter-spacing:2px;margin-bottom:12px;}
.products-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px;}
.product-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-decoration:none;transition:all 0.3s;display:flex;flex-direction:column;}
.product-card:hover{transform:translateY(-3px);border-color:var(--secondary);}
.product-card .p-img{width:100%;height:140px;background:linear-gradient(135deg,rgba(0,87,184,0.1),rgba(0,168,255,0.05));border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:36px;color:var(--border);margin-bottom:12px;}
.product-card h3{font-size:15px;font-weight:700;color:var(--text-primary);margin-bottom:4px;}
.product-card .model{font-size:12px;color:var(--text-muted);margin-bottom:6px;}
.product-card .desc{font-size:13px;color:var(--text-secondary);line-height:1.5;flex:1;}
.product-card .tag{display:inline-block;padding:2px 10px;background:rgba(0,87,184,0.12);border-radius:12px;font-size:11px;color:var(--secondary);align-self:flex-start;margin-top:8px;}
.placeholder-notice{text-align:center;padding:40px;background:var(--bg-card);border:1px dashed var(--border);border-radius:var(--radius);margin-top:32px;}
.placeholder-notice p{color:var(--text-secondary);margin-bottom:16px;}
@media(max-width:767px){.page-hero h1{font-size:28px;}}
</style>
</head>
<body>
<nav class="lj-nav">
  <div class="lj-nav-inner">
    <a href="/" class="lj-nav-brand"><span class="lj-nav-dot"></span><span>Longjiang Automation</span></a>
    <button class="lj-nav-toggle" id="ljNavToggle" aria-label="Menu"><span></span><span></span><span></span></button>
    <ul class="lj-nav-links" id="ljNavLinks">
      <li><a href="/en/">Home</a></li>
      <li class="lj-dropdown"><a href="javascript:void(0)" style="color:var(--text-primary);background:rgba(0,87,184,0.15);">Products ▼</a>
        <ul class="lj-dropdown-menu">
          <li><a href="/en/products/">All Products</a></li>
          <li><a href="/en/products/?cat=Winding+Machine">Winding Machine</a></li>
          <li><a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a></li>
        </ul>
      </li>
      <li><a href="/en/videos/">Videos</a></li>
      <li><a href="/en/cases/">Cases</a></li>
      <li><a href="/en/about/">About</a></li>
      <li><a href="/en/contact/" class="lj-nav-cta">\U0001f4de Contact</a></li>
      <li><a href="javascript:toggleLang()" class="lj-nav-lang">\U0001f310 中文</a></li>
    </ul>
  </div>
</nav>
<section class="page-hero">
  <span class="section-label">⚙ PRODUCTS</span>
  <h1>Our Products</h1>
  <p>37 models covering winding, assembly, and inspection</p>
</section>
<section class="section">
  <div class="section-inner">
    <div class="products-grid">
      <div class="product-card"><div class="p-img">⚙</div><h3>LJ-7HS-3 Dual-Spindle Winder</h3><div class="model">Dual-spindle · High-speed</div><div class="desc">For brushless motor stator winding, 30% efficiency gain</div><span class="tag">Winding Machine</span></div>
      <div class="product-card"><div class="p-img">\U0001f9f2</div><h3>18mm Inner Magnet Inserter</h3><div class="model">Inner rotor · Auto insertion</div><div class="desc">For 18mm inner rotor magnet assembly</div><span class="tag">Magnet Machine</span></div>
      <div class="product-card"><div class="p-img">⚙</div><h3>High-Speed 4-Spindle Winder</h3><div class="model">4-spindle · High efficiency</div><div class="desc">Four spindles winding simultaneously for mass production</div><span class="tag">Winding Machine</span></div>
      <div class="product-card"><div class="p-img">\U0001f4c4</div><h3>LJ-CZJ-Y01 Paper Inserter</h3><div class="model">Automatic paper insertion</div><div class="desc">For stator slot paper automatic insertion</div><span class="tag">Paper Inserter</span></div>
    </div>
    <div class="placeholder-notice">
      <p>Partial listing — 37 models available. Contact us for full catalog.</p>
      <a href="tel:18968693691" class="hero-btn hero-btn-primary">\U0001f4de Inquire +86 18968693691</a>
      <p style="color:var(--text-muted);font-size:12px;margin-top:12px;">Product images placeholder — replace with actual photos</p>
    </div>
  </div>
</section>
""" + EN_FOOTER + EN_FLOAT + WECHAT_MODAL + EN_SCRIPT + """
</body>
</html>"""

wp(os.path.join(PAGES_DIR, 'en', 'products', 'index.html'), en_products)
print("EN products written")

print("\n===== ALL PAGES INCLUDING ENGLISH WRITTEN SUCCESSFULLY =====")


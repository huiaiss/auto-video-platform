import os

src = r'D:\auto-video-platform\deploy\index.html'
dst = r'D:\auto-video-platform\deploy\en\index.html'

with open(src, 'r', encoding='utf-8') as f:
    html = f.read()

pairs = [
    ('lang="zh-CN"', 'lang="en"'),
    ('<title>台州隆江自动化设备有限公司 — 让绕线更智能</title>', '<title>Taizhou Longjiang Automation — Smarter Winding Solutions</title>'),
    ('<link rel="canonical" href="https://longjiang-ai.com/">', '<link rel="canonical" href="https://longjiang-ai.com/en/">'),
    ('hreflang="zh-CN"', 'hreflang="en"'),
    ('<meta property="og:title" content="台州隆江自动化设备有限公司 — 让绕线更智能">', '<meta property="og:title" content="Taizhou Longjiang Automation — Smarter Winding Solutions">'),
    ('<meta property="og:site_name" content="台州隆江自动化">', '<meta property="og:site_name" content="Longjiang Automation">'),
    ('"name": "台州隆江自动化设备有限公司"', '"name": "Taizhou Longjiang Automation Equipment Co., Ltd."'),
    ('"alternateName": "台州隆江自动化"', '"alternateName": "Longjiang Automation"'),
    ('"description": "自动化设备制造企业', '"description": "Automation equipment manufacturer'),
    ('"knowsAbout": ["绕线机", "无刷电机绕线机", "自动化设备", "磁钢机", "插纸机"]', '"knowsAbout": ["Winding Machine", "Brushless Motor Winder", "Automation Equipment", "Magnet Machine", "Paper Inserter"]'),
    ('<a href="/">首页</a>', '<a href="/en/">Home</a>'),
    ('产品 ▼', 'Products ▼'),
    ('<li><a href="/products/">全部产品</a></li>', '<li><a href="/en/products/">All Products</a></li>'),
    ('<li><a href="/products/?cat=绕线机">绕线机</a></li>', '<li><a href="/en/products/?cat=Winding Machine">Winding Machine</a></li>'),
    ('<li><a href="/products/?cat=磁钢机">磁钢机</a></li>', '<li><a href="/en/products/?cat=Magnet Machine">Magnet Machine</a></li>'),
    ('<li><a href="/products/?cat=插纸机">插纸机</a></li>', '<li><a href="/en/products/?cat=Paper Inserter">Paper Inserter</a></li>'),
    ('<li><a href="/products/?cat=其他">其他设备</a></li>', '<li><a href="/en/products/?cat=Other">Other</a></li>'),
    ('<a href="/videos/">视频</a>', '<a href="/en/videos/">Videos</a>'),
    ('<a href="/cases/">案例</a>', '<a href="/en/cases/">Cases</a>'),
    ('<a href="/about/">关于</a>', '<a href="/en/about/">About</a>'),
    ('<li><a href="/contact/" class="lj-nav-cta">📞 联系</a></li>', '<li><a href="/en/contact/" class="lj-nav-cta">📞 Contact</a></li>'),
    ('<a href="javascript:toggleLang()" class="lj-nav-lang">🌐 English</a>', '<a href="javascript:toggleLang()" class="lj-nav-lang">🌐 中文</a>'),
    ('<span class="lj-nav-name">台州隆江自动化</span>', '<span class="lj-nav-name">Longjiang Automation</span>'),
    ('源头工厂 · 省级科技型企业', 'Factory Direct · 13 Years Excellence'),
    ('让 <span class="highlight">绕线</span> 更智能', '<span class="highlight">Smarter</span> Winding Solutions'),
    ('台州隆江自动化 — 13年专注绕线机、磁钢机、插纸机研发制造<br>37款设备覆盖电机生产全工序，源头工厂直供，免费样机打样', 'Longjiang Automation — 13 years of winding, magnet & paper inserter expertise<br>37 models, factory-direct, free sample testing'),
    ('查看全部产品 →', 'View All Products →'),
    ('📞 18968693691', '📞 +86 18968693691'),
    ('热门设备推荐', 'Featured Equipment'),
    ('源头工厂直供 · 免费样机打样', 'Factory Direct · Free Sample Testing'),
    ('适合无刷电机定子绕线，生产效率提升30%', 'For brushless motor stator winding, 30% efficiency gain'),
    ('双工位 · 高速内绕', 'Dual-spindle · High-speed'),
    ('400mm中心距设计，适应更大规格定子绕线', '400mm center distance for larger stators'),
    ('400中心距 · 高精度', '400mm center · High precision'),
    ('500中心距 · 大规格', '500mm center · Large format'),
    ('超大中心距，满足大型电机定子生产需求', 'Extra-large center distance for big motor stators'),
    ('四工位 · 高效率', '4-spindle · High efficiency'),
    ('四工位同时绕线，大批量生产首选', '4 spindles simultaneously, ideal for mass production'),
    ('内转子 · 自动插磁钢', 'Inner rotor · Auto insertion'),
    ('适配18mm内转子磁钢自动装配', 'For 18mm inner rotor magnet assembly'),
    ('飞叉式 · 外绕', 'Flyer type · Outer winding'),
    ('外绕转子专用设备，双工位高效生产', 'Outer rotor specialist, dual-spindle efficient'),
    ('产品分类', 'Product Categories'),
    ('覆盖绕线、装配、检测全工序的自动化设备', 'Full-coverage automation for winding, assembly & inspection'),
    ('<a href="/products/?cat=绕线机" class="cat-card">', '<a href="/en/products/?cat=Winding+Machine" class="cat-card">'),
    ('<a href="/products/?cat=磁钢机" class="cat-card">', '<a href="/en/products/?cat=Magnet+Machine" class="cat-card">'),
    ('<a href="/products/?cat=插纸机" class="cat-card">', '<a href="/en/products/?cat=Paper+Inserter" class="cat-card">'),
    ('<a href="/products/?cat=其他" class="cat-card">', '<a href="/en/products/?cat=Other" class="cat-card">'),
    ('<div class="cat-name">绕线机</div>', '<div class="cat-name">Winding Machine</div>'),
    ('<div class="cat-name">磁钢机</div>', '<div class="cat-name">Magnet Machine</div>'),
    ('<div class="cat-name">插纸机</div>', '<div class="cat-name">Paper Inserter</div>'),
    ('<div class="cat-name">其他设备</div>', '<div class="cat-name">Other Equipment</div>'),
    ('<div class="cat-count">19 款设备</div>', '<div class="cat-count">19 Models</div>'),
    ('<div class="cat-count">16 款设备</div>', '<div class="cat-count">16 Models</div>'),
    ('<div class="cat-count">2 款设备</div>', '<div class="cat-count">2 Models</div>'),
    ('为什么选择隆江', 'Why Choose Longjiang'),
    ('年行业深耕', 'Years Experience'),
    ('2011年成立，持续专注电机自动化设备研发制造，积累深厚工艺经验', 'Founded in 2011, focused on motor automation R&D and manufacturing'),
    ('款设备矩阵', 'Equipment Models'),
    ('绕线机、磁钢机、插纸机等全系列覆盖，适配各种电机生产需求', 'Full series covering all motor production needs'),
    ('良品率保证', 'Yield Rate Guarantee'),
    ('精密伺服控制 + 自动检测系统，确保产品一致性和良品率', 'Precision servo control + auto inspection for consistent quality'),
    ('源头工厂直供', 'Factory Direct'),
    ('台州自有工厂生产，省去中间环节，品质可控、交期有保障', 'Own factory in Taizhou, no middlemen, guaranteed quality and delivery'),
    ('获取专属设备方案', 'Get Your Solution'),
    ('技术工程师 1 对 1 对接 · 免费提供样机打样', '1-on-1 Consultation · Free Sample Testing'),
    ('📞 立即致电 18968693691', '📞 Call +86 18968693691'),
    ('✉ 在线询价 / 获取方案', '✉ Online Inquiry'),
    ('产品中心', 'Products'),
    ('<a href="/products/?cat=绕线机">绕线机系列</a>', '<a href="/en/products/?cat=Winding+Machine">Winding Machine</a>'),
    ('<a href="/products/?cat=磁钢机">磁钢机系列</a>', '<a href="/en/products/?cat=Magnet+Machine">Magnet Machine</a>'),
    ('<a href="/products/?cat=插纸机">插纸机系列</a>', '<a href="/en/products/?cat=Paper+Inserter">Paper Inserter</a>'),
    ('<a href="/products/">全部设备</a>', '<a href="/en/products/">All Products</a>'),
    ('<a href="/about/">公司介绍</a>', '<a href="/en/about/">Company</a>'),
    ('<a href="/cases/">客户案例</a>', '<a href="/en/cases/">Case Studies</a>'),
    ('<a href="/service/">服务承诺</a>', '<a href="/en/service/">Service</a>'),
    ('📞 <a href="tel:18968693691">18968693691</a>', '📞 <a href="tel:18968693691">+86 18968693691</a>'),
    ('✉ 微信: ljzdh888', '✉ WeChat: ljzdh888'),
    ('📍 浙江台州椒江区刘洋工业园区', '📍 Jiaojiang, Taizhou, Zhejiang, China'),
    ('© 2026 台州隆江自动化设备有限公司 &nbsp;|&nbsp; 让绕线更智能', '© 2026 Taizhou Longjiang Automation | Smarter Winding Solutions'),
    ('制造业AI询盘工厂 — 让每一台设备被精准找到', 'Factory-Direct Automation Equipment'),
    ('📱 扫码添加微信 · 请用真实二维码替换', '📱 Scan for WeChat · Replace with real QR'),
    ('电话咨询', 'Call Us'),
    ('微信询价', 'WeChat'),
    ('获取方案', 'Get Quote'),
    ('微信号 ljzdh888 已复制，打开微信添加', 'WeChat: ljzdh888 copied'),
    ('扫码添加微信', 'Scan WeChat'),
    ('请用真实二维码替换 /assets/img/wechat-qr.jpg', 'Replace with real QR code'),
]

for old, new in pairs:
    html = html.replace(old, new)

# Fix carousel product tag labels
html = html.replace('绕线机</span>', 'Winding Machine</span>')
html = html.replace('磁钢机</span>', 'Magnet Machine</span>')

with open(dst, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Written: {dst} ({len(html)} bytes)')
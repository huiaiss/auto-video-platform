import os

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

styles = read_file('_deploy_styles.txt')
nav_cn = read_file('_deploy_nav.txt')
footer_cn = read_file('_deploy_footer.txt')
float_all = read_file('_deploy_float.txt')

nav_en = read_file('_deploy_en_nav.txt')
footer_en = read_file('_deploy_en_footer.txt')
float_en = read_file('_deploy_en_float.txt')

cn_pages = [
    ('contact', 'contact', read_file('_deploy_contact_cn.txt')),
    ('about', 'about', read_file('_deploy_about_cn.txt')),
    ('videos', 'videos', read_file('_deploy_videos_cn.txt')),
    ('cases', 'cases', read_file('_deploy_cases_cn.txt')),
    ('service', 'service', read_file('_deploy_service_cn.txt')),
]

en_pages = [
    ('contact', 'contact', read_file('_deploy_contact_en.txt')),
    ('about', 'about', read_file('_deploy_about_en.txt')),
    ('videos', 'videos', read_file('_deploy_videos_en.txt')),
    ('cases', 'cases', read_file('_deploy_cases_en.txt')),
    ('service', 'service', read_file('_deploy_service_en.txt')),
]

cn_titles = {
    'contact': '联系我们 | 台州隆江自动化设备有限公司',
    'about': '关于我们 | 台州隆江自动化设备有限公司',
    'videos': '设备视频 | 台州隆江自动化设备有限公司',
    'cases': '客户案例 | 台州隆江自动化设备有限公司',
    'service': '服务承诺 | 台州隆江自动化设备有限公司',
}

en_titles = {
    'contact': 'Contact Us | Longjiang Automation',
    'about': 'About Us | Longjiang Automation',
    'videos': 'Machine Videos | Longjiang Automation',
    'cases': 'Case Studies | Longjiang Automation',
    'service': 'Service | Longjiang Automation',
}

cn_desc = {
    'contact': '台州隆江自动化设备有限公司，24小时在线，欢迎来电或微信咨询。免费样机打样，非标定制。',
    'about': '台州隆江自动化设备有限公司，专注绕线机、磁钢机、插纸机等电机生产设备的研发制造，源头工厂直供。',
    'videos': '台州隆江自动化设备有限公司 — 绕线机、磁钢机、插纸机工作视频展示。',
    'cases': '台州隆江自动化设备有限公司 — 绕线机/磁钢机客户案例。',
    'service': '台州隆江自动化设备有限公司 — 售前咨询、免费打样、安装调试、售后保障。',
}

en_desc = {
    'contact': 'Taizhou Longjiang Automation Equipment Co., Ltd. 24/7 online. Call or WeChat for free sample testing.',
    'about': 'Taizhou Longjiang Automation Equipment Co., Ltd. — Winding Machine & Automation Equipment Manufacturer.',
    'videos': 'Watch our winding machines, magnet machines and paper inserters in action.',
    'cases': 'Customer success stories from Longjiang Automation winding machine deployments.',
    'service': 'Free sample testing, on-site installation & training, non-standard customization, 1-year warranty.',
}

def make_page_cn(name, title, desc, body):
    s = '<!DOCTYPE html>\n'
    s += '<html lang="zh-CN">\n'
    s += '<head>\n'
    s += '<meta charset="UTF-8">\n'
    s += '<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">\n'
    s += '<meta name="description" content="' + desc + '">\n'
    s += '<meta name="format-detection" content="telephone=yes">\n'
    s += '<title>' + title + '</title>\n'
    s += '<link rel="canonical" href="https://longjiang-ai.com/' + name + '/">\n'
    s += '<link rel="alternate" hreflang="zh-CN" href="https://longjiang-ai.com/' + name + '/">\n'
    s += '<link rel="alternate" hreflang="en" href="https://longjiang-ai.com/en/' + name + '/">\n'
    s += styles + '\n'
    s += '</head>\n<body>\n'
    s += nav_cn + '\n'
    s += '<main>\n' + body + '\n</main>\n'
    s += footer_cn + '\n'
    s += float_all + '\n'
    s += '</body>\n</html>'
    return s

def make_page_en(name, title, desc, body):
    s = '<!DOCTYPE html>\n'
    s += '<html lang="en">\n'
    s += '<head>\n'
    s += '<meta charset="UTF-8">\n'
    s += '<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">\n'
    s += '<meta name="description" content="' + desc + '">\n'
    s += '<meta name="format-detection" content="telephone=yes">\n'
    s += '<title>' + title + '</title>\n'
    s += '<link rel="canonical" href="https://longjiang-ai.com/en/' + name + '/">\n'
    s += '<link rel="alternate" hreflang="zh-CN" href="https://longjiang-ai.com/' + name + '/">\n'
    s += '<link rel="alternate" hreflang="en" href="https://longjiang-ai.com/en/' + name + '/">\n'
    s += styles + '\n'
    s += '</head>\n<body>\n'
    s += nav_en + '\n'
    s += '<main>\n' + body + '\n</main>\n'
    s += footer_en + '\n'
    s += float_en + '\n'
    s += '</body>\n</html>'
    return s

for name, _, body in cn_pages:
    html = make_page_cn(name, cn_titles[name], cn_desc[name], body)
    path = '_deploy/' + name + '/index.html'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('CN ' + name + ': ' + str(len(html)) + ' bytes')

for name, _, body in en_pages:
    html = make_page_en(name, en_titles[name], en_desc[name], body)
    path = '_deploy/en/' + name + '/index.html'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print('EN ' + name + ': ' + str(len(html)) + ' bytes')

print('\nAll placeholder pages assembled!')

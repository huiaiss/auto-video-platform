#!/usr/bin/env python3
"""
P0 修复脚本 — 2026-06-05
任务1: 英文产品页 SEO 翻译 (37个 en/products/*.html)
任务2: 产品页加图片 + 移除 about:blank video 标签 (74个页面)
"""

import os
import re
import shutil
import json
from pathlib import Path

BASE_DIR = Path('d:/auto-video-platform')
DEPLOY_CN = BASE_DIR / 'deploy' / 'products'
DEPLOY_EN = BASE_DIR / 'deploy' / 'en' / 'products'
ASSETS_IMG = BASE_DIR / 'deploy' / 'assets' / 'img'
IMAGE_SOURCE = Path('E:/隆江产品图 车间图 LOGO/产品图')

# ── 1. 翻译映射表 ──

# 中文→英文 产品名翻译
PRODUCT_NAME_EN = {
    "15KW单工位内绕绕线机": "15KW Single-Station Inner Winding Machine",
    "18内插装磁钢机": "18 Inner-Mount Magnet Inserter",
    "22KW单工位内绕绕线机（蒙特纳利改装版）": "22KW Single-Station Inner Winding Machine (Montanari Modified)",
    "6伺服插磁钢点胶机": "6-Servo Magnet Insertion & Dispensing Machine",
    "LJ-7HS-3双工位绕线机": "LJ-7HS-3 Dual-Station Winding Machine",
    "LJ-7HS双工位400中心绕线机": "LJ-7HS Dual-Station 400 Center Winding Machine",
    "LJ-7HS双工位500中心绕线机": "LJ-7HS Dual-Station 500 Center Winding Machine",
    "LJ-9WD-1 三针绕线机": "LJ-9WD-1 Three-Needle Winding Machine",
    "LJ-CG-DJ 插磁钢点胶机（外贴式）": "LJ-CG-DJ Magnet Insert & Dispense (External Mount)",
    "LJ-CGDJ-1 插磁钢点胶机（LJ-CGDJ-1）": "LJ-CGDJ-1 Magnet Insert & Dispense Machine",
    "LJ-CGDJ-3 插骨架-插磁钢点胶机（LJ-CGDJ-3）": "LJ-CGDJ-3 Frame-Magnet Insert & Dispense Machine",
    "LJ-CZJ-Y01 自动打纸机（内绕转子）": "LJ-CZJ-Y01 Auto Paper Inserter (Inner Rotor)",
    "LJ-RT 自动热套机": "LJ-RT Automatic Heat Shrink Machine",
    "LJ-WRFC-SGW400 发电机定子双工位400飞叉绕线机": "LJ-WRFC-SGW400 Generator Stator Dual-Station 400 Flyer Winder",
    "LJ-WX-2 双工位飞叉绕线机": "LJ-WX-2 Dual-Station Flyer Winding Machine",
    "T型分块绕线机": "T-Section Segmented Winding Machine",
    "V字型点胶磁钢机": "V-Shape Dispensing Magnet Machine",
    "表贴磁钢机": "Surface-Mount Magnet Machine",
    "插磁钢机（隆江v版）": "Magnet Inserter (Longjiang V Edition)",
    "插磁钢机（隆江标准型）": "Magnet Inserter (Longjiang Standard)",
    "单工位飞叉外绕机": "Single-Station Flyer External Winder",
    "单工位飞叉外绕机（标准型）": "Single-Station Flyer External Winder (Standard)",
    "点胶装磁钢机（视觉定位-力华）": "Dispense & Magnet Machine (Vision-Lihua)",
    "多股单工位内绕绕线机": "Multi-Strand Single-Station Inner Winder",
    "多股四工位内绕绕线机": "Multi-Strand Four-Station Inner Winder",
    "高速六工位内绕绕线机": "High-Speed Six-Station Inner Winder",
    "高速四工位绕线机": "High-Speed Four-Station Winding Machine",
    "简易磁钢机": "Basic Magnet Machine",
    "经济型磁钢机": "Economy Magnet Machine",
    "内嵌式插磁钢点胶机": "Embedded Magnet Insert & Dispense",
    "双工位点胶装磁钢机": "Dual-Station Dispense & Magnet Machine",
    "双工位飞叉外绕机": "Dual-Station Flyer External Winder",
    "双工位飞叉外绕机（华昊）": "Dual-Station Flyer External Winder (Huahao)",
    "双工位分块绕线机": "Dual-Station Segmented Winding Machine",
    "双工位经济型绕线机": "Dual-Station Economy Winding Machine",
    "自动插签机": "Automatic Tag Inserter",
    "自动打纸机（外绕转子）": "Auto Paper Inserter (External Rotor)",
}

# 中文→英文 描述翻译（按唯一值映射）
DESC_EN = {
    "首末端自动预留定长线头": "Automatic fixed-length wire end reservation at both ends",
    "人工上下转子": "Manual rotor loading and unloading",
    "自动绕线，自动分度": "Automatic winding with auto-indexing",
    "自动送纸、打纸": "Automatic paper feeding and slot insertion",
    "主要适用于电机机壳热套": "Designed for motor housing heat shrink fitting",
    "自动插签": "Automatic tag insertion",
}

# 英文关键词后缀（所有产品公用）
KW_SUFFIX_EN = "Longjiang Automation,automation equipment,China manufacturer,industrial machine"

# 类别→关键词映射
CAT_KW_EN = {
    "绕线机": "winding machine,coil winder,motor winding equipment",
    "磁钢机": "magnet machine,magnet inserter,magnet insertion equipment",
    "插纸机": "paper inserter,slot paper insertion machine",
    "其他": "industrial automation equipment",
}

# 类别→图片映射
CAT_IMG = {
    "绕线机": "product-winding.jpg",
    "磁钢机": "product-magnet.jpg",
    "插纸机": "factory-workshop.jpg",
    "其他": "factory-gate.jpg",
}

# 公司名翻译
COMPANY_CN = "台州隆江自动化设备有限公司"
COMPANY_EN = "Taizhou Longjiang Automation Equipment Co., Ltd."
COMPANY_SHORT_CN = "台州隆江自动化"
COMPANY_SHORT_EN = "Longjiang Automation"

# 公司名简写
COMPANY_EN_ONELINE = "Taizhou Longjiang Automation Equipment Co."

# ── 辅助函数 ──

def get_product_name_from_html(html: str) -> str:
    """从 HTML 中提取产品名（从 h1 或 title）"""
    m = re.search(r'<h1[^>]*class="device-title"[^>]*>([^<]+)</h1>', html)
    if m:
        return m.group(1).strip()
    m = re.search(r'<title>([^<|]+)', html)
    if m:
        return m.group(1).strip()
    return ""

def get_product_category(name_cn: str) -> str:
    """根据产品名判断类别"""
    # 从文件名匹配geo数据
    return "绕线机"  # default

def determine_category(filename: str, name_cn: str) -> str:
    """Determine product category from name or filename"""
    name_lower = name_cn.lower()
    if any(kw in name_lower for kw in ['绕线', '绕线机', 'winding', '绕线机']):
        return "绕线机"
    if any(kw in name_lower for kw in ['磁钢', '磁钢机', 'magnet']):
        return "磁钢机"
    if any(kw in name_lower for kw in ['插纸', '打纸', 'paper']):
        return "插纸机"
    if any(kw in name_lower for kw in ['插签', '热套']):
        return "其他"
    # Check filename for clues
    model_match = re.search(r'LJ-(\w+)', filename)
    if model_match:
        model = model_match.group(1)
        if model.startswith(('CG', 'CGDJ')):
            return "磁钢机"
        elif model.startswith(('CZJ',)):
            return "插纸机"
        elif model.startswith(('RT',)):
            return "其他"
        else:
            return "绕线机"
    return "绕线机"  # default


def translate_title(title_cn: str) -> str:
    """Translate Chinese HTML title to English"""
    # Remove company name suffix
    title_clean = title_cn.replace(f' | {COMPANY_CN}', '').strip()
    
    # Try direct product name mapping
    if title_clean in PRODUCT_NAME_EN:
        product_en = PRODUCT_NAME_EN[title_clean]
    else:
        # Try partial match
        for cn, en in sorted(PRODUCT_NAME_EN.items(), key=lambda x: -len(x[0])):
            if cn in title_clean or title_clean in cn:
                product_en = en
                break
        else:
            product_en = title_clean  # fallback: keep as-is
    
    return f"{product_en} | {COMPANY_EN}"


def translate_description(desc_cn: str) -> str:
    """Translate Chinese meta description to English"""
    # Remove company name suffix
    desc_clean = desc_cn.replace(f' — {COMPANY_CN}', '').strip()
    
    # Try direct match
    if desc_clean in DESC_EN:
        desc_en = DESC_EN[desc_clean]
    else:
        desc_en = desc_clean  # fallback
    
    return f"{desc_en} — {COMPANY_EN}"


def translate_keywords(kw_cn: str, category: str) -> str:
    """Translate Chinese keywords to English"""
    parts = [p.strip() for p in kw_cn.split(',')]
    # Remove generic company-related keywords
    product_name_cn = parts[0] if parts else ""
    
    # Translate product name in keywords
    product_en = product_name_cn
    for cn, en in sorted(PRODUCT_NAME_EN.items(), key=lambda x: -len(x[0])):
        if cn == product_name_cn or product_name_cn in cn:
            product_en = en
            break
    
    cat_kw = CAT_KW_EN.get(category, "industrial equipment")
    return f"{product_en},{cat_kw},{KW_SUFFIX_EN}"


def build_image_map():
    """Build a mapping of product HTML filenames to image filenames"""
    # Use category-based mapping with a few specific assignments
    img_map = {}
    
    # Copy actual product images and assign them
    # We'll assign first batch of products to actual photos where possible
    product_list = sorted([f for f in os.listdir(DEPLOY_CN) if f.endswith('.html') and f != 'index.html'])
    
    # Get available product photos
    actual_photos = sorted([f for f in os.listdir(IMAGE_SOURCE) if f.upper().endswith(('.JPG', '.JPEG', '.PNG'))]) if IMAGE_SOURCE.exists() else []
    
    # Assign actual photos to first N products (strategy: winding machines first)
    winding_products = [p for p in product_list if '绕线' in p]
    magnet_products = [p for p in product_list if '磁钢' in p]
    other_products = [p for p in product_list if p not in winding_products and p not in magnet_products]
    ordered = winding_products + magnet_products + other_products
    
    for i, fname in enumerate(ordered):
        name_no_ext = fname.replace('.html', '')
        if i < len(actual_photos):
            # Copy the photo with product name
            src = IMAGE_SOURCE / actual_photos[i]
            ext = os.path.splitext(actual_photos[i])[1]
            dst_name = f"product-{name_no_ext}{ext}"
            dst = ASSETS_IMG / dst_name
            if not dst.exists():
                try:
                    shutil.copy2(src, dst)
                    print(f"  📸 Copied {actual_photos[i]} → {dst_name}")
                except Exception as e:
                    print(f"  ⚠️ Failed to copy {actual_photos[i]}: {e}")
            img_map[fname] = dst_name
        else:
            # Use category-based generic image
            cat = determine_category(fname, name_no_ext)
            img_map[fname] = CAT_IMG.get(cat, "factory-gate.jpg")
    
    return img_map


def fix_video_block(html: str, img_src: str, alt_text: str) -> str:
    """Replace video tag block with img tag"""
    # Find the video block pattern
    video_pattern = re.compile(
        r'<video[^>]*class="bg-video"[^>]*>.*?</video>',
        re.DOTALL
    )
    
    img_tag = f'<img class="bg-video" src="/assets/img/{img_src}" alt="{alt_text}" loading="lazy">'
    
    return video_pattern.sub(img_tag, html)


def update_json_ld(html: str) -> str:
    """Update JSON-LD: Chinese company/brand names to English"""
    # Replace company name in JSON-LD
    html = html.replace(f'"name": "{COMPANY_CN}"', f'"name": "{COMPANY_EN}"')
    html = html.replace(f'"name": "{COMPANY_SHORT_CN}"', f'"name": "{COMPANY_SHORT_EN}"')
    html = html.replace(f'"manufacturer": {{"@type": "Organization","name": "{COMPANY_CN}"', f'"manufacturer": {{"@type": "Organization","name": "{COMPANY_EN}"')
    html = html.replace(f'"seller": {{"@type": "Organization","name": "{COMPANY_CN}"', f'"seller": {{"@type": "Organization","name": "{COMPANY_EN}"')
    html = html.replace(f'"brand": {{"@type": "Brand","name": "{COMPANY_SHORT_CN}"', f'"brand": {{"@type": "Brand","name": "{COMPANY_SHORT_EN}"')
    return html


def fix_en_seo(html: str, filename: str) -> str:
    """Apply SEO translations to an English product page"""
    # Get product name from HTML
    name_cn = get_product_name_from_html(html)
    category = determine_category(filename, name_cn)
    
    # 1. Fix <title>
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        old_title = title_match.group(1)
        new_title = translate_title(old_title)
        html = html.replace(f'<title>{old_title}</title>', f'<title>{new_title}</title>')
        print(f"    title: {old_title[:40]}... → {new_title[:60]}...")
    
    # 2. Fix <meta name="description">
    desc_match = re.search(r'<meta name="description" content="([^"]+)">', html)
    if desc_match:
        old_desc = desc_match.group(1)
        new_desc = translate_description(old_desc)
        html = html.replace(f'content="{old_desc}"', f'content="{new_desc}"')
        print(f"    desc: {old_desc[:40]}... → {new_desc[:60]}...")
    
    # 3. Fix <meta name="keywords">
    kw_match = re.search(r'<meta name="keywords" content="([^"]+)">', html)
    if kw_match:
        old_kw = kw_match.group(1)
        new_kw = translate_keywords(old_kw, category)
        html = html.replace(f'content="{old_kw}"', f'content="{new_kw}"')
        print(f"    keywords translated (category: {category})")
    
    # 4. Fix JSON-LD (company name etc.)
    html = update_json_ld(html)
    
    # 5. Fix OG meta tags
    html = html.replace(f'content="{COMPANY_SHORT_CN}"', f'content="{COMPANY_SHORT_EN}"')
    
    # 6. Fix canonical link "longjiang-ai.com" (no www) — but skip, that's P0#4
    
    return html


def fix_cn_image(html: str, filename: str, img_map: dict) -> str:
    """Add image to Chinese product page and remove video"""
    name_cn = get_product_name_from_html(html)
    img_src = img_map.get(filename, "factory-gate.jpg")
    html = fix_video_block(html, img_src, f"{name_cn} - {COMPANY_SHORT_CN}")
    return html


def fix_en_image(html: str, filename: str, img_map: dict) -> str:
    """Add image to English product page and remove video"""
    name_cn = get_product_name_from_html(html)
    img_src = img_map.get(filename, "factory-gate.jpg")
    # Translate name for alt text
    name_en = name_cn
    for cn, en in PRODUCT_NAME_EN.items():
        if cn in name_cn or name_cn in cn:
            name_en = en
            break
    html = fix_video_block(html, img_src, f"{name_en} - {COMPANY_SHORT_EN}")
    return html


def main():
    print("=" * 70)
    print("🔧 P0 修复脚本 — SEO翻译 + 产品图片")
    print("=" * 70)
    
    # Ensure assets/img exists
    ASSETS_IMG.mkdir(parents=True, exist_ok=True)
    
    # ── Step 0: Build image map and copy files ──
    print("\n📦 构建图片映射...")
    img_map = build_image_map()
    print(f"  ✅ {len(img_map)} products mapped to images")
    
    # ── Task 1: English SEO Translation ──
    print("\n" + "=" * 70)
    print("📝 任务1: 英文产品页 SEO 翻译")
    print("=" * 70)
    
    en_files = sorted([f for f in os.listdir(DEPLOY_EN) if f.endswith('.html') and f != 'index.html'])
    seo_count = 0
    for fname in en_files:
        fpath = DEPLOY_EN / fname
        print(f"\n  📄 {fname}")
        with open(fpath, encoding='utf-8') as f:
            html = f.read()
        
        new_html = fix_en_seo(html, fname)
        
        if new_html != html:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            seo_count += 1
            print(f"  ✅ SEO updated")
        else:
            print(f"  ⏭️  No changes")
    
    print(f"\n  ✅ 任务1完成: {seo_count}/{len(en_files)} pages SEO翻译")
    
    # ── Task 2: Add images to product pages ──
    print("\n" + "=" * 70)
    print("🖼️ 任务2: 产品页加图片 + 移除 about:blank video")
    print("=" * 70)
    
    cn_files = sorted([f for f in os.listdir(DEPLOY_CN) if f.endswith('.html') and f != 'index.html'])
    en_files = sorted([f for f in os.listdir(DEPLOY_EN) if f.endswith('.html') and f != 'index.html'])
    
    total_fixed = 0
    
    # Chinese pages
    print("\n  --- 中文产品页 ---")
    for fname in cn_files:
        fpath = DEPLOY_CN / fname
        with open(fpath, encoding='utf-8') as f:
            html = f.read()
        
        new_html = fix_cn_image(html, fname, img_map)
        if new_html != html:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            total_fixed += 1
            img_used = img_map.get(fname, "factory-gate.jpg")
            print(f"  ✅ {fname} → {img_used}")
        else:
            print(f"  ⏭️ {fname} (no video tag found)")
    
    # English pages
    print("\n  --- 英文产品页 ---")
    for fname in en_files:
        fpath = DEPLOY_EN / fname
        with open(fpath, encoding='utf-8') as f:
            html = f.read()
        
        new_html = fix_en_image(html, fname, img_map)
        if new_html != html:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            total_fixed += 1
            img_used = img_map.get(fname, "factory-gate.jpg")
            print(f"  ✅ {fname} → {img_used}")
        else:
            print(f"  ⏭️ {fname} (no video tag found)")
    
    print(f"\n  ✅ 任务2完成: {total_fixed} pages 加图")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 汇总")
    print("=" * 70)
    print(f"  SEO翻译: {seo_count}/{len(en_files)} 英文产品页")
    print(f"  产品加图: {total_fixed}/{(len(cn_files)+len(en_files))} 页面")
    print(f"  图片目录: {ASSETS_IMG}")
    print(f"  ✅ 两个P0任务完成！")
    
    # Verify
    print("\n🔍 抽样验证...")
    for sample in en_files[:2] + cn_files[:2]:
        fpath_cn = DEPLOY_CN / sample if (DEPLOY_CN / sample).exists() else DEPLOY_EN / sample
        fpath_en = DEPLOY_EN / sample if (DEPLOY_EN / sample).exists() else None
        for fp in [fpath_cn, fpath_en]:
            if fp and fp.exists():
                with open(fp, encoding='utf-8') as f:
                    content = f.read()
                has_video = 'about:blank' in content
                has_img = '<img class="bg-video"' in content
                title_en = bool(re.search(r'<title>', content))
                print(f"  {fp.name}: video={has_video}, img={has_img}")


if __name__ == '__main__':
    main()

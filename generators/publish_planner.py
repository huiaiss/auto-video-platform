"""
publish_planner.py - 四平台发布策略生成器
输入: script.json + brand config
输出: publish_plan.json（标题/标签/时间/封面/评论）
"""

import json, os
from pathlib import Path
from datetime import datetime

BEST_TIMES = {
    "douyin":     ["11:30", "20:00", "21:00"],
    "kuaishou":   ["07:00", "19:00", "20:30"],
    "xiaohongshu":["12:00", "20:00", "21:30"],
    "shipinhao":  ["12:00", "20:00", "22:00"],
}

TITLE_TEMPLATES = {
    "douyin": {
        "hook":      "{product}的{spec}，同行看了都说牛",
        "pain":      "做了{year}年{industry}才发现，{pain_point}",
        "curiosity": "{product}内部什么样？今天带你看看",
        "identity":  "干{industry}的都懂，这个{spec}意味着什么",
        "data":      "{product}：{data_point}，这就是天花板",
    },
    "kuaishou": {
        "hook":      "带你们看看{product}是怎么干活的",
        "pain":      "{product}效率翻倍，不用加班了",
        "curiosity": "这个{spec}一出来，同行坐不住了",
        "identity":  "搞{industry}的兄弟，这个见过没",
    },
    "xiaohongshu": {
        "hook":      "工厂实拍|{product}的工作日常",
        "pain":      "做{industry}的姐妹，这个真的可以",
        "curiosity": "{product}的{spec}怎么做到的",
        "identity":  "制造业日常|{product}干货分享",
    },
    "shipinhao": {
        "hook":      "{brand_name}：{product}用数据说话",
        "pain":      "{product}效率提升{data_point}",
        "curiosity": "{product}的{spec}实测结果来了",
        "identity":  "{year}年经验，告诉你{product}怎么选",
    },
}

PLATFORM_TAGS = {
    "douyin":     ["#自动化设备", "#智能制造", "#工厂实拍", "#制造业", "#工业自动化"],
    "kuaishou":   ["#自动化设备", "#工厂实拍", "#制造业", "#机械设备"],
    "xiaohongshu":["#自动化设备", "#工厂", "#制造业干货", "#设备分享", "#工业设计"],
    "shipinhao":  ["#自动化设备", "#智能工厂", "#中国制造", "#制造业", "#工业4.0"],
}

def _pick_hook_type(script):
    emotions = [b.get("emotion", "") for b in script.get("beats", [])]
    if "pain" in emotions:
        return "pain"
    if any("效率" in b.get("text", "") or "%" in b.get("text", "") for b in script.get("beats", [])):
        return "data"
    title = script.get("title", "")
    if "揭秘" in title or "秘密" in title:
        return "curiosity"
    return "hook"

def generate(script_path: str, brand: dict) -> dict:
    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    brand_name = brand.get("brand_name", "")
    products = brand.get("main_products", [{"name": "自动化设备"}])
    product_name = products[0]["name"] if products else "自动化设备"
    industry = brand.get("industry", "制造业")
    year = brand.get("founded", 2010)
    age = 2026 - year
    tags = brand.get("tags", [])
    default_tags = brand.get("output", {}).get("hashtags", [])

    specs = products[0].get("specs", {}) if products else {}
    spec_list = list(specs.values()) if isinstance(specs, dict) else []
    first_spec = spec_list[0] if spec_list else "精密制造"

    data_points = []
    for b in script.get("beats", []):
        text = b.get("text", "")
        for kw in ["%", "倍", "万", "秒", "分钟"]:
            if kw in text:
                for part in text.split("。"):
                    if kw in part and len(part) < 20:
                        data_points.append(part.strip())
                        break
                if data_points:
                    break
    data_point = data_points[0] if data_points else "效率大幅提升"

    pain_points = [
        f"{product_name}效率提不上去",
        f"{product_name}精度不够",
        f"{product_name}良品率上不去",
    ]
    pain_point = pain_points[hash(product_name + industry) % len(pain_points)]

    def fill(tmpl):
        return tmpl.format(
            brand_name=brand_name,
            product=product_name,
            industry=industry,
            spec=first_spec,
            year=age,
            pain_point=pain_point,
            data_point=data_point,
        )

    hook_type = _pick_hook_type(script)
    platforms = {}

    for platform in ["douyin", "kuaishou", "xiaohongshu", "shipinhao"]:
        tmpls = TITLE_TEMPLATES.get(platform, {})
        tmpl = tmpls.get(hook_type, tmpls.get("hook", ""))
        title = fill(tmpl)
        max_len = {"douyin": 30, "kuaishou": 25, "xiaohongshu": 20, "shipinhao": 30}
        if len(title) > max_len.get(platform, 30):
            title = title[:max_len[platform]-1] + "…"

        platform_tags = PLATFORM_TAGS.get(platform, [])
        brand_tags = [f"#{t}" if not t.startswith("#") else t for t in tags[:3]]
        industry_tags = default_tags[:3]
        all_tags = list(dict.fromkeys(brand_tags + industry_tags + platform_tags))[:5]
        hashtags = " ".join(all_tags)

        desc_map = {
            "douyin":     f"{product_name}实拍，{data_point}。{brand_name}让你看看真正的{first_spec}。#制造业 #工厂实拍",
            "kuaishou":   f"{product_name}干活视频来了！{data_point}，老铁们觉得怎么样？#制造业 #工厂实拍",
            "xiaohongshu":f"工厂实拍|{product_name}的工作日常。{data_point}。干货分享，点赞收藏。#制造业 #自动化设备",
            "shipinhao":  f"{brand_name} - {product_name}实拍展示。{data_point}。用数据和事实说话。",
        }

        cover = {
            "douyin":     {"ratio": "3:4", "width": 1080, "height": 1440, "style": "品牌色+大字标题+产品图"},
            "kuaishou":   {"ratio": "1:1", "width": 1080, "height": 1080, "style": "标题占上1/3+产品特写"},
            "xiaohongshu":{"ratio": "3:4", "width": 1080, "height": 1440, "style": "精致排版+多图拼接"},
            "shipinhao":  {"ratio": "1:1", "width": 1080, "height": 1080, "style": "信任元素突出+品牌Logo"},
        }

        comments = [
            {"type": "引导互动", "text": f"你们厂的{product_name}效率怎么样？评论区聊聊"},
            {"type": "种草咨询", "text": f"想了解{product_name}参数的，私信发你选型方案"},
            {"type": "讨论触发", "text": f"做了{age}年{industry}，你觉得自动化是趋势还是噱头？"},
            {"type": "隐藏转化", "text": f"需要{product_name}资料的朋友，评论区扣1"},
        ]

        platforms[platform] = {
            "title": title,
            "description": desc_map.get(platform, ""),
            "hashtags": hashtags,
            "best_time": BEST_TIMES.get(platform, ["12:00"]),
            "cover": cover.get(platform),
            "comments": comments,
        }

    return {
        "generated_at": datetime.now().isoformat(),
        "brand": brand_name,
        "product": product_name,
        "video_title": script.get("title", ""),
        "video_duration_s": script.get("total_duration_s", 30),
        "platforms": platforms,
        "notes": [
            "发布时间按工业品采购决策者活跃时段",
            "标题字数：抖音≤30/快手≤25/小红书≤20/视频号≤30",
            "禁用词：最、第一、100%、全网、唯一",
            "AI生成内容需标注"
        ],
    }

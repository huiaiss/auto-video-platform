"""品牌配置加载器 — 消灭硬编码 'AI照妖镜'。

Usage:
    from config.brand_loader import get_brand
    brand = get_brand()
    name = brand["brand_name"]  # 当前激活品牌
"""

import json, os

_CONFIG_CACHE: dict | None = None
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))

# 默认品牌配置文件
DEFAULT_BRAND_FILE = "brand_dna.json"


def get_brand(brand_key: str = None) -> dict:
    """加载品牌 DNA 配置。

    不加参数返回当前激活品牌（config/brand_dna.json）。
    传 brand_key 加载 configs/brands/{key}.json。
    """
    global _CONFIG_CACHE

    if brand_key:
        # 尝试 configs/brands/{key}.json
        brands_dir = os.path.join(os.path.dirname(_CONFIG_DIR), "configs", "brands")
        path = os.path.join(brands_dir, f"{brand_key}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        # fallback: config/brand_{key}.json
        path = os.path.join(_CONFIG_DIR, f"brand_{brand_key}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)

    if _CONFIG_CACHE is None:
        path = os.path.join(_CONFIG_DIR, DEFAULT_BRAND_FILE)
        with open(path, encoding="utf-8") as f:
            _CONFIG_CACHE = json.load(f)
    return _CONFIG_CACHE


def get_brand_name() -> str:
    """快捷方法：只取品牌名称。"""
    return get_brand().get("brand_name", "AI照妖镜")


def get_slogan() -> str:
    """快捷方法：只取 slogan。"""
    return get_brand().get("slogan", "")


def get_outro_template() -> str:
    """快捷方法：结尾口播模板。"""
    return get_brand().get("outro_template", "")


def get_tags() -> list[str]:
    """快捷方法：默认话题标签。"""
    return get_brand().get("tags", [])


def reset_cache():
    """清空缓存（切换品牌后调用）。"""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None

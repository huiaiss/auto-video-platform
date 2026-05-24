"""Image Compositor — product-on-scene compositing engine.

Takes product images + scene backgrounds + creative brief params → composited product shots.

Pipeline per product image:
  1. rembg background removal → transparent PNG
  2. Resize to target scale on scene
  3. Composite onto scene background with shadow
  4. Apply color grading from creative brief palette
  5. Multi-platform crop/resize

Usage:
    from builders.image_compositor import ImageCompositor
    comp = ImageCompositor()
    result = comp.composite(product_path, scene_path, config)
"""

import os
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


# ─── Data Types ─────────────────────────────────────────────

@dataclass
class CompositeConfig:
    """Configuration for a single composite operation."""
    product_path: str
    scene_path: str
    output_dir: str
    # Product placement (normalized 0.0–1.0)
    position: tuple[float, float] = (0.5, 0.55)  # (x, y) center of product
    scale: float = 0.55  # product height / canvas height
    # Shadow
    shadow_enabled: bool = True
    shadow_opacity: int = 80
    shadow_offset: tuple[int, int] = (8, 16)
    shadow_blur: int = 12
    # Color grading
    brightness: float = 1.05
    contrast: float = 1.05
    saturation: float = 1.0
    # Output
    canvas_size: tuple[int, int] = (1080, 1920)  # (w, h)
    platform: str = "douyin"
    # Brand
    brand_color: Optional[str] = None  # hex accent for border/overlay


@dataclass
class CompositeResult:
    """Result of a composite operation."""
    output_path: str
    product_path: str
    scene_path: str
    canvas_size: tuple[int, int]
    platform: str


# ─── Platform Dimensions ────────────────────────────────────

PLATFORM_SIZES = {
    "douyin": (1080, 1920),
    "kuaishou": (1080, 1920),
    "shipinhao": (1080, 1920),
    "xiaohongshu": (1080, 1440),
    "pdd": (1080, 1440),
    "taobao": (800, 800),
    "jingdong": (800, 800),
}


# ─── Compositor ─────────────────────────────────────────────

class ImageCompositor:
    """Product-on-scene image compositing engine."""

    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir) if cache_dir else None

    # ─── Public API ─────────────────────────────────────

    def composite_one(self, config: CompositeConfig) -> CompositeResult:
        """Composite a single product image onto a scene background."""
        product = self._load_image(config.product_path)
        scene = self._load_and_resize_scene(config.scene_path, config.canvas_size)

        # Step 1: Remove background from product
        product_no_bg = self._remove_background(product)

        # Step 2: Scale product to target size
        product_scaled = self._scale_product(product_no_bg, config.canvas_size, config.scale)

        # Step 3: Build composite canvas
        canvas = scene.copy()

        # Step 4: Calculate position
        px, py = self._calc_position(config.position, product_scaled, config.canvas_size)

        # Step 5: Draw shadow
        if config.shadow_enabled:
            canvas = self._draw_shadow(
                canvas, product_scaled, (px, py),
                config.shadow_offset, config.shadow_blur, config.shadow_opacity,
            )

        # Step 6: Paste product onto canvas
        canvas.paste(product_scaled, (px, py), product_scaled)

        # Step 7: Apply color grading
        canvas = self._apply_grading(canvas, config)

        # Step 8: Save
        output_path = self._save_output(canvas, config)
        return CompositeResult(
            output_path=output_path,
            product_path=config.product_path,
            scene_path=config.scene_path,
            canvas_size=config.canvas_size,
            platform=config.platform,
        )

    def composite_batch(
        self,
        product_paths: list[str],
        scene_paths: list[str],
        configs: list[CompositeConfig] = None,
        base_config: CompositeConfig = None,
        output_dir: str = None,
    ) -> list[CompositeResult]:
        """Composite multiple product images across multiple scenes.

        If configs is provided, uses those directly.
        Otherwise generates configs as: product × scene cartesian product.
        """
        results = []
        if configs:
            for cfg in configs:
                if output_dir:
                    cfg.output_dir = output_dir
                results.append(self.composite_one(cfg))
        elif base_config:
            for product_path in product_paths:
                for scene_path in scene_paths:
                    cfg = CompositeConfig(
                        product_path=product_path,
                        scene_path=scene_path,
                        output_dir=output_dir or base_config.output_dir,
                        position=base_config.position,
                        scale=base_config.scale,
                        shadow_enabled=base_config.shadow_enabled,
                        canvas_size=base_config.canvas_size,
                        platform=base_config.platform,
                        brand_color=base_config.brand_color,
                    )
                    results.append(self.composite_one(cfg))
        return results

    def composite_for_platforms(
        self,
        product_path: str,
        scene_path: str,
        platforms: list[str],
        base_config: CompositeConfig = None,
        output_dir: str = None,
    ) -> list[CompositeResult]:
        """Generate platform-adapted variants of the same composite."""
        results = []
        for platform in platforms:
            size = PLATFORM_SIZES.get(platform, (1080, 1920))
            cfg = CompositeConfig(
                product_path=product_path,
                scene_path=scene_path,
                output_dir=output_dir or (base_config.output_dir if base_config else "."),
                position=base_config.position if base_config else (0.5, 0.55),
                scale=base_config.scale if base_config else 0.55,
                canvas_size=size,
                platform=platform,
                brand_color=base_config.brand_color if base_config else None,
            )
            results.append(self.composite_one(cfg))
        return results

    # ─── Internal Methods ─────────────────────────────────

    @staticmethod
    def _load_image(path: str) -> Image.Image:
        img = Image.open(path).convert("RGBA")
        return img

    @staticmethod
    def _load_and_resize_scene(path: str, canvas_size: tuple[int, int]) -> Image.Image:
        scene = Image.open(path).convert("RGBA")
        if scene.size != canvas_size:
            scene = scene.resize(canvas_size, Image.LANCZOS)
        return scene

    @staticmethod
    def _remove_background(img: Image.Image) -> Image.Image:
        """Remove background using rembg."""
        try:
            from rembg import remove
            # rembg works with PIL images directly
            return remove(img)
        except Exception:
            # Fallback: return original if rembg fails
            return img

    @staticmethod
    def _scale_product(img: Image.Image, canvas_size: tuple[int, int], scale: float) -> Image.Image:
        """Scale product to target fraction of canvas height."""
        cw, ch = canvas_size
        target_h = int(ch * scale)
        ratio = target_h / img.height
        target_w = int(img.width * ratio)
        # Don't exceed canvas width
        if target_w > cw * 0.9:
            target_w = int(cw * 0.9)
            ratio = target_w / img.width
            target_h = int(img.height * ratio)
        return img.resize((target_w, target_h), Image.LANCZOS)

    @staticmethod
    def _calc_position(
        pos: tuple[float, float],
        product: Image.Image,
        canvas_size: tuple[int, int],
    ) -> tuple[int, int]:
        """Calculate top-left pixel position from normalized center position."""
        cw, ch = canvas_size
        pw, ph = product.size
        cx = int(cw * pos[0])
        cy = int(ch * pos[1])
        return (cx - pw // 2, cy - ph // 2)

    @staticmethod
    def _draw_shadow(
        canvas: Image.Image,
        product: Image.Image,
        product_pos: tuple[int, int],
        offset: tuple[int, int],
        blur: int,
        opacity: int,
    ) -> Image.Image:
        """Draw a soft drop shadow beneath the product."""
        px, py = product_pos
        pw, ph = product.size

        # Create shadow from product alpha mask
        alpha = product.split()[-1]
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)

        # Offset and blur
        sx, sy = px + offset[0], py + offset[1]
        shadow_alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
        # Reduce opacity
        shadow_alpha = shadow_alpha.point(lambda p: min(p, opacity))

        shadow.paste((0, 0, 0, 0), (sx, sy), shadow_alpha)
        # Fill with black at alpha opacity
        shadow_colored = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        for y in range(canvas.height):
            for x in range(canvas.width):
                a = shadow.getpixel((x, y))[3]
                if a > 0:
                    shadow_colored.putpixel((x, y), (0, 0, 0, a))

        return Image.alpha_composite(canvas, shadow_colored)

    @staticmethod
    def _apply_grading(img: Image.Image, config: CompositeConfig) -> Image.Image:
        """Apply brightness/contrast/saturation adjustments."""
        # Convert to RGB for enhancement operations
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
        else:
            rgb = img.convert("RGB")

        if config.brightness != 1.0:
            rgb = ImageEnhance.Brightness(rgb).enhance(config.brightness)
        if config.contrast != 1.0:
            rgb = ImageEnhance.Contrast(rgb).enhance(config.contrast)
        if config.saturation != 1.0:
            rgb = ImageEnhance.Color(rgb).enhance(config.saturation)

        if img.mode == "RGBA":
            r, g, b = rgb.split()
            return Image.merge("RGBA", (r, g, b, a))
        return rgb.convert("RGBA")

    def _save_output(self, img: Image.Image, config: CompositeConfig) -> str:
        """Save composited image with a content-based filename."""
        content_fp = f"{config.product_path}|{config.scene_path}|{config.platform}|{config.canvas_size}"
        short_hash = hashlib.md5(content_fp.encode()).hexdigest()[:8]
        product_stem = Path(config.product_path).stem[:20]
        scene_stem = Path(config.scene_path).stem[:20]
        filename = f"comp_{product_stem}_on_{scene_stem}_{config.platform}_{short_hash}.png"
        os.makedirs(config.output_dir, exist_ok=True)
        output_path = os.path.join(config.output_dir, filename)
        img.save(output_path, "PNG", optimize=True)
        return output_path

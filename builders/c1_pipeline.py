"""C1 Pipeline — product image generation orchestrator.

End-to-end pipeline:
  Product Images → Product Analysis → Creative Brief → Scene Generation
  → Product-on-Scene Compositing → Multi-Platform Adaptation → Delivery

Integrates with visual-hub services (creative_engine, scene_generator) and
the auto-video-platform image_compositor.

Usage:
    from builders.c1_pipeline import C1Pipeline
    pipeline = C1Pipeline(output_dir="output/c1_ep1")
    results = pipeline.run(product_images=["p1.png", "p2.png"], industry="鞋类")
"""

import os
import sys
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Ensure visual-hub is importable
_VISUAL_HUB = r"C:\Users\Administrator\visual-hub"
if _VISUAL_HUB not in sys.path:
    sys.path.insert(0, _VISUAL_HUB)


# ─── Data Types ─────────────────────────────────────────────

@dataclass
class C1Result:
    """Result of a C1 pipeline run."""
    output_dir: str
    product_analysis: dict
    creative_brief: dict
    scene_paths: list[str]
    composite_paths: list[dict]  # [{product, scene, platform, path}]
    total_images: int
    total_time_s: float
    ok: bool


# ─── Pipeline ───────────────────────────────────────────────

class C1Pipeline:
    """Orchestrates the full product image generation pipeline."""

    def __init__(self, output_dir: str = "output/c1"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_dir = self.output_dir / "scenes"
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.composites_dir = self.output_dir / "composites"
        self.composites_dir.mkdir(parents=True, exist_ok=True)

    # ─── Public API ─────────────────────────────────────

    def run(
        self,
        product_images: list[str],
        industry: str = "鞋类",
        platforms: list[str] = None,
        creative_brief: dict = None,
        product_analysis: dict = None,
        skip_analysis: bool = False,
    ) -> C1Result:
        """Run the full C1 pipeline.

        Args:
            product_images: List of product photo paths
            industry: Product category for AI analysis
            platforms: Target platforms (default: ["douyin", "xiaohongshu"])
            creative_brief: Pre-computed brief (skips AI call if provided)
            product_analysis: Pre-computed analysis (skips AI call if provided)
            skip_analysis: Skip AI analysis entirely (use cached data)

        Returns:
            C1Result with all output paths and metadata
        """
        t_start = time.time()
        if platforms is None:
            platforms = ["douyin", "xiaohongshu", "taobao"]

        # Phase 1: Product Analysis
        t1 = time.time()
        if not skip_analysis and not product_analysis:
            product_analysis = self._run_analysis(product_images, industry)
        phase1_s = round(time.time() - t1, 2)

        # Phase 2: Creative Brief
        t2 = time.time()
        if not skip_analysis and not creative_brief and product_analysis:
            creative_brief = self._run_brief(product_analysis, industry)
        phase2_s = round(time.time() - t2, 2)

        # Phase 3: Scene Generation
        t3 = time.time()
        scene_paths = self._generate_scenes(creative_brief, product_analysis)
        phase3_s = round(time.time() - t3, 2)

        # Phase 4: Compositing
        t4 = time.time()
        composite_paths = self._composite_all(product_images, scene_paths, platforms, creative_brief)
        phase4_s = round(time.time() - t4, 2)

        total_time = round(time.time() - t_start, 2)

        result = C1Result(
            output_dir=str(self.output_dir),
            product_analysis=product_analysis or {},
            creative_brief=creative_brief or {},
            scene_paths=scene_paths,
            composite_paths=composite_paths,
            total_images=len(composite_paths),
            total_time_s=total_time,
            ok=len(composite_paths) > 0,
        )

        # Save metadata
        self._save_metadata(result, {
            "phase_timings": {
                "1_analysis": phase1_s,
                "2_brief": phase2_s,
                "3_scenes": phase3_s,
                "4_compositing": phase4_s,
                "total": total_time,
            }
        })

        return result

    # ─── Phase Implementations ────────────────────────────

    def _run_analysis(self, product_images: list[str], industry: str) -> dict:
        """Run product analysis via creative_engine (Doubao Vision)."""
        try:
            from services.creative_engine import analyze_product
            print(f"  [C1] Running product analysis on {len(product_images)} images...")
            result = analyze_product(product_images, industry)
            print(f"  [C1] Analysis complete: {result.get('category', '?')} / {result.get('sub_category', '?')}")
            return result
        except ImportError:
            print("  [C1] creative_engine not available, using placeholder analysis")
            return {}
        except Exception as e:
            print(f"  [C1] Analysis failed: {e}")
            return {}

    def _run_brief(self, product_analysis: dict, industry: str) -> dict:
        """Run creative brief generation via creative_engine (DeepSeek)."""
        try:
            from services.creative_engine import generate_creative_brief
            print("  [C1] Generating creative brief...")
            result = generate_creative_brief(product_analysis, industry)
            print(f"  [C1] Brief: {result.get('concept_name', '?')} — {len(result.get('scenes', []))} scenes")
            return result
        except ImportError:
            print("  [C1] creative_engine not available, using placeholder brief")
            return {}
        except Exception as e:
            print(f"  [C1] Brief generation failed: {e}")
            return {}

    def _generate_scenes(self, creative_brief: dict, product_analysis: dict = None) -> list[str]:
        """Generate scene backgrounds from creative brief."""
        scenes = creative_brief.get("scenes", []) if creative_brief else []
        if not scenes:
            # Fallback: generate default scenes
            print("  [C1] No scenes in brief, generating 3 default scenes")
            scenes = [
                {"scene_name": "窗边白墙", "description": "简约白墙，自然光从窗户洒入"},
                {"scene_name": "咖啡厅角落", "description": "温暖咖啡厅，下午阳光"},
                {"scene_name": "纯色背景", "description": "干净素色背景，产品突出"},
            ]

        color_palette = creative_brief.get("color_palette", {}) if creative_brief else {}

        try:
            from services.scene_generator import generate_scene

            scene_paths = []
            for i, scene in enumerate(scenes):
                if isinstance(scene, dict):
                    name = scene.get("scene_name", f"scene_{i+1}")
                    desc = scene.get("description", name)
                else:
                    name = str(scene)
                    desc = name

                print(f"  [C1] Generating scene {i+1}/{len(scenes)}: {name}")
                path = generate_scene(name, desc, color_palette, resolution="portrait")
                if path and os.path.exists(path):
                    scene_paths.append(path)
                else:
                    print(f"  [C1] WARNING: Scene '{name}' generation returned no file")

            return scene_paths
        except ImportError:
            print("  [C1] scene_generator not available")
            return []
        except Exception as e:
            print(f"  [C1] Scene generation failed: {e}")
            return []

    def _composite_all(
        self,
        product_images: list[str],
        scene_paths: list[str],
        platforms: list[str],
        creative_brief: dict = None,
    ) -> list[dict]:
        """Composite all product×scene×platform combinations."""
        from builders.image_compositor import ImageCompositor, CompositeConfig

        compositor = ImageCompositor()
        color_palette = creative_brief.get("color_palette", {}) if creative_brief else {}
        accent = color_palette.get("accent", "")

        results = []
        total = len(product_images) * len(scene_paths) * len(platforms)
        count = 0

        for product_path in product_images:
            for scene_path in scene_paths:
                for platform in platforms:
                    count += 1
                    from builders.image_compositor import PLATFORM_SIZES
                    size = PLATFORM_SIZES.get(platform, (1080, 1920))
                    config = CompositeConfig(
                        product_path=product_path,
                        scene_path=scene_path,
                        output_dir=str(self.composites_dir),
                        canvas_size=size,
                        platform=platform,
                        brand_color=accent,
                    )
                    try:
                        result = compositor.composite_one(config)
                        results.append({
                            "product": os.path.basename(product_path),
                            "scene": os.path.basename(scene_path),
                            "platform": platform,
                            "path": result.output_path,
                        })
                    except Exception as e:
                        print(f"  [C1] Composite failed [{count}/{total}]: {e}")

        print(f"  [C1] Composited {len(results)}/{total} images")
        return results

    # ─── Metadata ─────────────────────────────────────────

    def _save_metadata(self, result: C1Result, extra: dict = None):
        """Save pipeline run metadata as JSON."""
        meta = {
            "output_dir": result.output_dir,
            "total_images": result.total_images,
            "total_time_s": result.total_time_s,
            "scene_count": len(result.scene_paths),
            "composite_count": len(result.composite_paths),
            "composites": result.composite_paths,
        }
        if extra:
            meta.update(extra)
        meta_path = self.output_dir / "c1_metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

"""Builders layer — storyboard config → HyperFrames HTML composition.

Components: reusable visual blocks (social-frame, glitch, zoom-analyze, compare, outro).
CompositionBuilder: assembles components into a complete, renderable HTML file.
SubtitleEngine: kinetic typography (word-by-word/char-by-char pop).
SFXSystem: sound effects auto-trigger rules.
AssetPipeline: multi-source asset matching (local → AI gen → stock).
AssemblyEngine: end-to-end video assembly (TTS → HTML → export).

Usage:
    from builders import CompositionBuilder, load_components
    builder = CompositionBuilder(style="ai_flaw_detect")
    html = builder.build(storyboard_json, timing_json)
"""

from .composition_builder import CompositionBuilder, StoryboardConfig
from .components import COMPONENT_REGISTRY, Component, load_components
from .sfx_library import SFX_REGISTRY, SFXEntry, list_available_sfx, resolve_sfx_path
from .storyboard_mapper import StoryboardMapper
from .subtitle_engine import STYLE_PRESETS, SubtitleEngine, SubtitleStyle
from .asset_pipeline import AssetPipeline, AssetRef, AssetPlan, plan_to_storyboard
from .assembly_engine import AssemblyEngine, AssemblyResult, quick_assemble

__all__ = [
    "CompositionBuilder",
    "StoryboardConfig",
    "COMPONENT_REGISTRY",
    "Component",
    "load_components",
    "SFX_REGISTRY",
    "SFXEntry",
    "list_available_sfx",
    "resolve_sfx_path",
    "StoryboardMapper",
    "STYLE_PRESETS",
    "SubtitleEngine",
    "SubtitleStyle",
    "AssetPipeline",
    "AssetRef",
    "AssetPlan",
    "plan_to_storyboard",
    "AssemblyEngine",
    "AssemblyResult",
    "quick_assemble",
]

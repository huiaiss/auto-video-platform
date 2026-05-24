"""SFX Library — sound effect registry with auto-trigger rules.

Each SFX entry maps an sfx_id to a file path and optional metadata.
The SFX_TRIGGERS dict provides auto-match rules so the CompositionBuilder
can automatically select sounds based on animation context.

Usage:
    from builders.sfx_library import SFX_REGISTRY, resolve_sfx_path
    path = resolve_sfx_path("ding_01")  # → "assets/sfx/ding_01.mp3"
"""

import os
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class SFXEntry:
    """A registered sound effect."""
    sfx_id: str                          # unique id, e.g. "ding_01"
    file_path: str                       # relative path from project root
    description: str = ""                # human-readable description
    category: str = "ui"                 # "ui" | "impact" | "whoosh" | "glitch" | "ambient"
    duration_s: float = 0.3              # estimated duration
    default_volume: float = 0.7          # 0.0–1.0

    @property
    def exists(self) -> bool:
        """Check if the file exists on disk (best-effort)."""
        return os.path.exists(self.file_path)


# ---------------------------------------------------------------------------
# SFX Registry — all available sounds
# ---------------------------------------------------------------------------

SFX_REGISTRY: dict[str, SFXEntry] = {
    # ── UI / Notification ──
    "ding_01": SFXEntry(
        sfx_id="ding_01",
        file_path="assets/sfx/ding_01.mp3",
        description="Short UI ding — marker placed, checkmark hit",
        category="ui",
        duration_s=0.15,
    ),
    "ding_02": SFXEntry(
        sfx_id="ding_02",
        file_path="assets/sfx/ding_02.mp3",
        description="Softer ding — subtler UI feedback",
        category="ui",
        duration_s=0.12,
    ),
    "ping_01": SFXEntry(
        sfx_id="ping_01",
        file_path="assets/sfx/ping_01.mp3",
        description="High ping — neon circle marker appears",
        category="ui",
        duration_s=0.2,
    ),

    # ── Impact / Reveal ──
    "impact_01": SFXEntry(
        sfx_id="impact_01",
        file_path="assets/sfx/impact_01.mp3",
        description="Heavy impact — big reveal text hits",
        category="impact",
        duration_s=0.5,
    ),
    "impact_02": SFXEntry(
        sfx_id="impact_02",
        file_path="assets/sfx/impact_02.mp3",
        description="Medium impact — secondary reveal",
        category="impact",
        duration_s=0.35,
    ),

    # ── Whoosh / Motion ──
    "whoosh_01": SFXEntry(
        sfx_id="whoosh_01",
        file_path="assets/sfx/whoosh_01.mp3",
        description="Fast whoosh — keyword tag pops in, zoom start",
        category="whoosh",
        duration_s=0.3,
    ),
    "whoosh_02": SFXEntry(
        sfx_id="whoosh_02",
        file_path="assets/sfx/whoosh_02.mp3",
        description="Slower whoosh — panel slide-in, compare scene",
        category="whoosh",
        duration_s=0.4,
    ),

    # ── Glitch / Digital ──
    "glitch_01": SFXEntry(
        sfx_id="glitch_01",
        file_path="assets/sfx/glitch_01.mp3",
        description="Subtle glitch spark — first hint before transition",
        category="glitch",
        duration_s=0.2,
    ),
    "glitch_02": SFXEntry(
        sfx_id="glitch_02",
        file_path="assets/sfx/glitch_02.mp3",
        description="Big glitch crunch — main transition hit",
        category="glitch",
        duration_s=0.4,
    ),

    # ── Ambient / Background ──
    "scan_hum": SFXEntry(
        sfx_id="scan_hum",
        file_path="assets/sfx/scan_hum.mp3",
        description="Low hum — scan overlay active",
        category="ambient",
        duration_s=2.0,
        default_volume=0.2,
    ),
    "tension_rise": SFXEntry(
        sfx_id="tension_rise",
        file_path="assets/sfx/tension_rise.mp3",
        description="Building tension drone — before big reveal",
        category="ambient",
        duration_s=3.0,
        default_volume=0.25,
    ),
}

# ── Convenience lookup ───────────────────────────────────────

SFX_BY_CATEGORY: dict[str, list[SFXEntry]] = {}
for _entry in SFX_REGISTRY.values():
    SFX_BY_CATEGORY.setdefault(_entry.category, []).append(_entry)


def resolve_sfx_path(sfx_id: str, base_dir: str = ".") -> str:
    """Resolve an sfx_id to its absolute file path."""
    entry = SFX_REGISTRY.get(sfx_id)
    if entry is None:
        raise KeyError(f"Unknown SFX id '{sfx_id}'. Available: {list(SFX_REGISTRY)}")
    return os.path.join(base_dir, entry.file_path)


def list_available_sfx(category: Optional[str] = None) -> list[SFXEntry]:
    """List all available SFX, optionally filtered by category."""
    if category:
        return SFX_BY_CATEGORY.get(category, [])
    return list(SFX_REGISTRY.values())

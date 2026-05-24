"""E-commerce component library — product showcase, feature highlight, social proof.

Independent from components.py (AI flaw detect). Uses the same Component protocol
but a completely different visual language: warm commercial aesthetics, brand-aware
color system, product-centric narrative beats.

Component set:
  hook-reveal      — Opening: product reveal with big title + price anchor
  feature-highlight — Zoom into product detail + feature tag chips
  scene-lifestyle   — Product in real environment with mood text
  before-after      — "Before vs After" split-screen transformation
  trust-signal      — Social proof: stats, guarantees, testimonials
  cta-outro        — End card: brand logo, save/follow/comment CTAs

Registry: ECOMMERCE_REGISTRY (separate from COMPONENT_REGISTRY in components.py)
"""

from dataclasses import dataclass, field
from typing import Optional

# Re-use base types from core components module
from .components import Component, SFXTrigger, SubtitleLine


# ---------------------------------------------------------------------------
# E-commerce Component Registry (independent from AI flaw detect registry)
# ---------------------------------------------------------------------------

ECOMMERCE_REGISTRY: dict[str, type[Component]] = {}


def _register(cls: type[Component]) -> type[Component]:
    ECOMMERCE_REGISTRY[cls.name] = cls
    return cls


# ---------------------------------------------------------------------------
# Component implementations
# ---------------------------------------------------------------------------


@_register
class HookRevealComponent(Component):
    """Opening hook — full-screen product reveal with dramatic title + price anchor.

    Visual arc: dark bg → product image fades in → title text slams in → price tag pops.
    Uses brand primary color for accent, warm gradient for atmosphere.

    Config keys:
        img_src: str         — product image path
        title_text: str      — main hook line (e.g. "这双老爹鞋穿上秒变大长腿")
        subtitle_text: str   — secondary line (e.g. "复古厚底 · 隐形增高5cm")
        price_text: str      — price reveal (e.g. "¥299" or "工厂价")
        price_original: str  — crossed-out original price (optional)
    """

    name = "hook-reveal"

    def css(self) -> str:
        return """
        .hr-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:radial-gradient(ellipse at 50% 35%, #1a1a2e 0%, #0a0a14 70%);
        }
        .hr-img-wrap {
            position:absolute;top:120px;left:50%;margin-left:-420px;
            width:840px;height:840px;border-radius:24px;overflow:hidden;
            box-shadow:0 20px 80px rgba(0,0,0,0.5);
        }
        .hr-img-wrap img {
            width:100%;height:100%;object-fit:cover;
        }
        .hr-title {
            position:absolute;top:1020px;left:60px;right:60px;
            color:#fff;font-size:58px;font-weight:900;text-align:center;
            line-height:1.3;text-shadow:0 4px 24px rgba(0,0,0,0.6);
            letter-spacing:0.02em;
        }
        .hr-subtitle {
            position:absolute;top:1160px;left:60px;right:60px;
            color:var(--brand-primary, #e8b45a);font-size:34px;font-weight:600;
            text-align:center;opacity:0.9;
        }
        .hr-price-tag {
            position:absolute;top:1280px;left:50%;margin-left:-140px;
            width:280px;height:90px;border-radius:20px;
            background:var(--brand-primary, #e8b45a);color:#1a1a14;
            display:flex;align-items:center;justify-content:center;
            font-size:48px;font-weight:900;letter-spacing:0.03em;
            box-shadow:0 8px 40px rgba(232,180,90,0.4);
        }
        .hr-price-original {
            position:absolute;top:1390px;left:50%;
            transform:translateX(-50%);
            color:#666;font-size:28px;text-decoration:line-through;
            text-align:center;
        }
        .hr-gradient-bottom {
            position:absolute;bottom:0;left:0;width:1080px;height:500px;
            background:linear-gradient(to top,rgba(10,10,20,0.95) 0%,rgba(10,10,20,0.4) 50%,transparent 100%);
        }
        """

    def html(self) -> str:
        c = self.config
        img = c.get("img_src", c.get("asset_path", ""))
        title = c.get("title_text", c.get("caption", "产品揭晓"))
        subtitle = c.get("subtitle_text", "")
        price = c.get("price_text", "")
        orig_price = c.get("price_original", "")

        price_html = ""
        if price:
            price_html = f'<div class="hr-price-tag" id="hrPrice">{price}</div>'
        orig_html = ""
        if orig_price:
            orig_html = f'<div class="hr-price-original" id="hrOrig">{orig_price}</div>'

        return f"""
        <div class="hr-bg" id="hrBg"></div>
        <div class="hr-img-wrap" id="hrImgW">
            <img src="{img}" id="hrImg" />
        </div>
        <div class="hr-title" id="hrTitle">{title}</div>
        <div class="hr-subtitle" id="hrSub">{subtitle}</div>
        {price_html}
        {orig_html}
        <div class="hr-gradient-bottom"></div>
        """

    def gsap(self) -> str:
        t = self.start
        dur = self.duration
        lines = f"""
        // Hook reveal @ {t:.1f}s
        tl.set("#hrBg",{{opacity:0}},{t});
        tl.to("#hrBg",{{opacity:1,duration:0.5,ease:"power3.out"}},{t+0.05});
        tl.from("#hrImgW",{{opacity:0,scale:0.88,y:30,duration:0.7,ease:"power3.out"}},{t+0.15});
        tl.to("#hrImg",{{scale:1.06,duration:{dur-0.5},ease:"none"}},{t+0.3});
        tl.from("#hrTitle",{{opacity:0,y:40,duration:0.55,ease:"back.out(1.5)"}},{t+0.45});
        tl.to("#hrTitle",{{scale:1.03,duration:0.25,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+1.0});
        """
        if self.config.get("subtitle_text"):
            lines += f'tl.from("#hrSub",{{opacity:0,y:20,duration:0.45,ease:"power3.out"}},{t+1.3});\n'
        if self.config.get("price_text"):
            lines += f'tl.from("#hrPrice",{{opacity:0,scale:0.3,duration:0.5,ease:"back.out(2)"}},{t+1.6});\n'
            lines += f'tl.to("#hrPrice",{{scale:1.06,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+2.2});\n'
        if self.config.get("price_original"):
            lines += f'tl.from("#hrOrig",{{opacity:0,duration:0.4,ease:"power3.out"}},{t+2.0});\n'
        return lines

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        triggers = [SFXTrigger("whoosh_01", t + 0.15, 0.6)]
        if self.config.get("price_text"):
            triggers.append(SFXTrigger("ding_01", t + 1.6, 0.7))
        return triggers


@_register
class FeatureHighlightComponent(Component):
    """Product feature close-up — smooth zoom + rotating highlight markers + tag chips.

    Visual arc: product image zooms into detail area → circular highlight pulses →
    feature tag chips pop in one by one → detail badge slides in from right.

    Config keys:
        img_src: str           — product image path
        zoom_origin_x/y: int   — transform-origin for zoom
        zoom_scale: float      — max zoom level (e.g. 2.2)
        feature_label: str     — section label (e.g. "材质细节")
        features: list[dict]   — [{label: str, top: int, left: int, delay: float}]
        highlight: dict        — {x, y, w, h} circular highlight position
        detail_badge: dict     — {text: str, sub_text: str, top: int}
    """

    name = "feature-highlight"

    def css(self) -> str:
        return """
        .fh-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:#0a0a14;
        }
        .fh-highlight-ring {
            position:absolute;border-radius:50%;z-index:12;pointer-events:none;
            border:4px solid var(--brand-primary, #e8b45a);
            box-shadow:0 0 40px rgba(232,180,90,0.5),0 0 80px rgba(232,180,90,0.2);
        }
        .fh-feature-chip {
            position:absolute;z-index:13;pointer-events:none;
            background:rgba(0,0,0,0.85);color:#fff;
            font-size:30px;font-weight:700;padding:14px 28px;border-radius:14px;
            border:1px solid var(--brand-primary, #e8b45a);
            box-shadow:0 4px 20px rgba(0,0,0,0.5);
            white-space:nowrap;
        }
        .fh-feature-chip::before {
            content:'';display:inline-block;width:10px;height:10px;
            border-radius:50%;background:var(--brand-primary, #e8b45a);
            margin-right:12px;vertical-align:middle;
        }
        .fh-detail-badge {
            position:absolute;z-index:14;pointer-events:none;
            background:rgba(0,0,0,0.9);color:#fff;
            padding:18px 30px;border-radius:16px;
            border:1px solid rgba(255,255,255,0.1);
            text-align:right;
        }
        .fh-detail-big {
            font-size:44px;font-weight:900;display:block;
            color:var(--brand-primary, #e8b45a);
            line-height:1.2;
        }
        .fh-detail-sub {
            font-size:26px;color:#999;margin-top:4px;
        }
        .fh-section-label {
            position:absolute;top:60px;left:60px;z-index:11;
            color:var(--brand-primary, #e8b45a);font-size:28px;font-weight:700;
            letter-spacing:0.12em;padding:10px 24px;border-radius:10px;
            background:rgba(232,180,90,0.08);border:1px solid rgba(232,180,90,0.2);
        }
        """

    def html(self) -> str:
        c = self.config
        img_id = c.get("img_id", f"fh_img_{int(self.start)}")
        ox = c.get("zoom_origin_x", 540)
        oy = c.get("zoom_origin_y", 700)
        label = c.get("feature_label", "产品细节")

        # Highlight ring
        hl = c.get("highlight", {})
        hl_html = ""
        if hl:
            hl_id = c.get("highlight_id", f"fh_hl_{int(self.start)}")
            hl_html = f'<div class="fh-highlight-ring" id="{hl_id}" style="width:{hl["w"]}px;height:{hl["h"]}px;top:{hl["y"]-hl["h"]//2}px;left:{hl["x"]-hl["w"]//2}px;"></div>'

        # Feature chips
        chips_html = ""
        for i, f in enumerate(c.get("features", [])):
            fid = f.get("id", f"fh_chip_{i}")
            chips_html += f'<div class="fh-feature-chip" id="{fid}" style="top:{f["top"]}px;left:{f["left"]}px;">{f["label"]}</div>\n'

        # Detail badge
        badge_html = ""
        db = c.get("detail_badge")
        if db:
            bid = c.get("badge_id", f"fh_badge_{int(self.start)}")
            badge_html = f"""
            <div class="fh-detail-badge" id="{bid}" style="top:{db.get('top',1400)}px;right:{db.get('right',60)}px;">
                <span class="fh-detail-big">{db.get('text','')}</span>
                <span class="fh-detail-sub">{db.get('sub_text','')}</span>
            </div>
            """

        return f"""
        <div class="fh-bg"></div>
        <div style="width:1080px;height:1920px;overflow:hidden;position:absolute;">
            <img src="{c.get('img_src', c.get('asset_path', ''))}"
                 style="position:absolute;width:1080px;height:1920px;object-fit:cover;will-change:transform;transform-origin:{ox}px {oy}px;"
                 id="{img_id}" />
        </div>
        <div style="position:absolute;bottom:0;left:0;width:1080px;height:600px;background:linear-gradient(to top,rgba(10,10,20,0.95),rgba(10,10,20,0.4),transparent);"></div>
        <div class="fh-section-label" id="fhLbl_{int(self.start)}">{label}</div>
        {hl_html}
        {chips_html}
        {badge_html}
        """

    def gsap(self) -> str:
        t = self.start
        c = self.config
        img_id = c.get("img_id", f"fh_img_{int(t)}")
        scale = c.get("zoom_scale", 2.2)
        lbl_id = f"fhLbl_{int(t)}"

        lines = f"""
        // Feature highlight @ {t:.1f}s
        tl.set("#{img_id}",{{scale:1}},{t});
        tl.to("#{img_id}",{{scale:{scale},duration:1.8,ease:"power3.inOut"}},{t+0.1});
        tl.from("#{lbl_id}",{{opacity:0,x:-20,duration:0.4,ease:"power3.out"}},{t+0.4});
        """

        # Highlight ring
        hl_id = c.get("highlight_id", f"fh_hl_{int(t)}")
        if c.get("highlight"):
            lines += f"""
        tl.from("#{hl_id}",{{opacity:0,scale:0.3,duration:0.5,ease:"back.out(2)"}},{t+1.2});
        tl.to("#{hl_id}",{{scale:1.1,duration:0.6,repeat:3,yoyo:true,ease:"sine.inOut"}},{t+1.7});
        """

        # Feature chips (staggered)
        for i, f in enumerate(c.get("features", [])):
            fid = f.get("id", f"fh_chip_{i}")
            delay = f.get("delay", 1.5 + i * 0.6)
            lines += f'tl.from("#{fid}",{{opacity:0,scale:0.5,y:-10,duration:0.4,ease:"back.out(1.5)"}},{t+delay});\n'

        # Detail badge
        if c.get("detail_badge"):
            bid = c.get("badge_id", f"fh_badge_{int(t)}")
            bd = c.get("badge_delay", 3.0)
            lines += f'tl.from("#{bid}",{{opacity:0,x:50,duration:0.5,ease:"power3.out"}},{t+bd});\n'

        return "\n".join(lines)

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        triggers = [SFXTrigger("whoosh_01", t + 0.1, 0.5)]
        for i, f in enumerate(self.config.get("features", [])):
            delay = f.get("delay", 1.5 + i * 0.6)
            triggers.append(SFXTrigger("ping_01", t + delay, 0.5))
        return triggers


@_register
class SceneLifestyleComponent(Component):
    """Product in real environment — scene background + product overlay + mood text.

    Visual arc: blurry scene bg sharpens → product image slides in → mood tag fades up →
    scene description text appears at bottom.

    Config keys:
        scene_img: str      — background scene image
        product_img: str    — product overlay image (smaller, positioned)
        mood_text: str      — emotional tagline (e.g. "午后慢时光")
        scene_desc: str     — scene description (e.g. "咖啡厅角落 · 阳光正好")
        product_scale: float — product image scale (default 0.55)
        product_offset_y: int — vertical offset for product (default -80)
    """

    name = "scene-lifestyle"

    def css(self) -> str:
        return """
        .sl-scene-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
        }
        .sl-scene-bg img {
            width:100%;height:100%;object-fit:cover;
        }
        .sl-product-overlay {
            position:absolute;z-index:5;
            filter:drop-shadow(0 20px 60px rgba(0,0,0,0.5));
        }
        .sl-mood-tag {
            position:absolute;z-index:6;
            color:#fff;font-size:52px;font-weight:900;
            text-shadow:0 4px 20px rgba(0,0,0,0.7);
            letter-spacing:0.04em;
        }
        .sl-scene-desc {
            position:absolute;z-index:6;
            background:rgba(0,0,0,0.7);color:#fff;
            font-size:30px;font-weight:600;padding:16px 32px;
            border-radius:16px;text-align:center;
            border:1px solid rgba(255,255,255,0.08);
        }
        .sl-gradient-bottom {
            position:absolute;bottom:0;left:0;width:1080px;height:500px;
            background:linear-gradient(to top,rgba(0,0,0,0.85) 0%,rgba(0,0,0,0.3) 50%,transparent 100%);
            z-index:4;
        }
        """

    def html(self) -> str:
        c = self.config
        scene = c.get("scene_img", c.get("asset_path", ""))
        product = c.get("product_img", scene)  # fallback to scene img
        mood = c.get("mood_text", "")
        desc = c.get("scene_desc", "")
        prod_scale = c.get("product_scale", 0.55)
        prod_oy = c.get("product_offset_y", -80)

        # Center product overlay
        pw = int(1080 * prod_scale)
        ph = int(1920 * prod_scale)
        px = (1080 - pw) // 2
        py = (1920 - ph) // 2 + prod_oy

        return f"""
        <div class="sl-scene-bg" id="slScene">
            <img src="{scene}" />
        </div>
        <div class="sl-gradient-bottom"></div>
        <div class="sl-product-overlay" id="slProduct" style="width:{pw}px;height:{ph}px;top:{py}px;left:{px}px;">
            <img src="{product}" style="width:100%;height:100%;object-fit:contain;" />
        </div>
        <div class="sl-mood-tag" id="slMood" style="top:280px;left:60px;">{mood}</div>
        <div class="sl-scene-desc" id="slDesc" style="bottom:180px;left:50%;transform:translateX(-50%);">{desc}</div>
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Scene lifestyle @ {t:.1f}s
        tl.set("#slScene",{{opacity:0.6,scale:1.08}},{t});
        tl.to("#slScene",{{opacity:1,scale:1,duration:1.2,ease:"power3.out"}},{t+0.1});
        tl.from("#slProduct",{{opacity:0,y:60,scale:0.9,duration:0.8,ease:"power3.out"}},{t+0.5});
        """
        if self.config.get("mood_text"):
            lines += f'tl.from("#slMood",{{opacity:0,y:-30,duration:0.6,ease:"power3.out"}},{t+0.9});\n'
        if self.config.get("scene_desc"):
            lines += f'tl.from("#slDesc",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+1.5});\n'
        # subtle product float
        lines += f'tl.to("#slProduct",{{y:"-=12",duration:2,ease:"sine.inOut",yoyo:true,repeat:1}},{t+1.0});\n'
        return lines


@_register
class BeforeAfterComponent(Component):
    """Side-by-side transformation — "before vs after" or "普通 vs 这双鞋".

    Visual arc: divider line sweeps in → left panel slides from left →
    right panel slides from right → "VS" badge pops → result text reveals.

    Config keys:
        before_img: str     — left/before image
        after_img: str      — right/after image
        before_label: str   — left label (e.g. "普通搭配")
        after_label: str    — right label (e.g. "穿上这双鞋")
        result_text: str    — bottom conclusion (e.g. "腿长瞬间+5cm")
    """

    name = "before-after"

    def css(self) -> str:
        return """
        .ba-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:#0a0a14;
        }
        .ba-panel {
            position:absolute;top:120px;width:500px;height:1100px;
            border-radius:20px;overflow:hidden;
            box-shadow:0 12px 50px rgba(0,0,0,0.5);
        }
        .ba-panel img {
            width:100%;height:100%;object-fit:cover;
        }
        .ba-label {
            position:absolute;top:16px;left:16px;
            padding:8px 20px;border-radius:20px;
            font-size:28px;font-weight:700;
        }
        .ba-label-before {
            background:rgba(255,255,255,0.12);color:#999;
            border:1px solid rgba(255,255,255,0.1);
        }
        .ba-label-after {
            background:var(--brand-primary, #e8b45a);color:#1a1a14;
        }
        .ba-divider {
            position:absolute;top:560px;left:50%;margin-left:-50px;
            width:100px;height:100px;border-radius:50%;
            background:rgba(0,0,0,0.85);border:2px solid rgba(255,255,255,0.2);
            display:flex;align-items:center;justify-content:center;
            color:var(--brand-primary, #e8b45a);font-size:40px;font-weight:900;
            z-index:5;
        }
        .ba-result {
            position:absolute;top:1260px;left:60px;right:60px;
            text-align:center;z-index:6;
        }
        .ba-result-text {
            display:inline-block;background:rgba(0,0,0,0.78);
            border-radius:20px;padding:24px 44px;
            border:1px solid var(--brand-primary, #e8b45a);
            color:#fff;font-size:46px;font-weight:700;
            text-shadow:0 2px 12px rgba(0,0,0,0.8);
        }
        """

    def html(self) -> str:
        c = self.config
        before_img = c.get("before_img", c.get("asset_path", ""))
        after_img = c.get("after_img", before_img)
        before_label = c.get("before_label", "改造前")
        after_label = c.get("after_label", "改造后")
        result = c.get("result_text", "")

        result_html = ""
        if result:
            result_html = f"""
            <div class="ba-result" id="baResult">
                <div class="ba-result-text">{result}</div>
            </div>
            """

        return f"""
        <div class="ba-bg"></div>
        <div class="ba-panel" id="baBefore" style="left:30px;">
            <img src="{before_img}" />
            <div class="ba-label ba-label-before">{before_label}</div>
        </div>
        <div class="ba-panel" id="baAfter" style="right:30px;">
            <img src="{after_img}" />
            <div class="ba-label ba-label-after">{after_label}</div>
        </div>
        <div class="ba-divider" id="baDiv">VS</div>
        {result_html}
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Before-after @ {t:.1f}s
        tl.from("#baBefore",{{opacity:0,x:-80,duration:0.7,ease:"power3.out"}},{t+0.2});
        tl.from("#baAfter",{{opacity:0,x:80,duration:0.7,ease:"power3.out"}},{t+0.2});
        tl.from("#baDiv",{{opacity:0,scale:0.2,duration:0.5,ease:"back.out(2)"}},{t+0.6});
        tl.to("#baDiv",{{scale:1.1,duration:0.4,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+1.2});
        tl.to("#baBefore img",{{scale:1.04,duration:5,ease:"none"}},{t+0.3});
        tl.to("#baAfter img",{{scale:1.04,duration:5,ease:"none"}},{t+0.3});
        """
        if self.config.get("result_text"):
            lines += f'tl.from("#baResult",{{opacity:0,y:30,duration:0.55,ease:"power3.out"}},{t+1.8});\n'
        return lines


@_register
class TrustSignalComponent(Component):
    """Social proof & trust building — stats, guarantees, testimonials grid.

    Visual arc: section title fades in → stat cards pop in staggered →
    guarantee badge slides up → testimonial quote fades in.

    Config keys:
        title: str           — section title (e.g. "为什么选择我们")
        stats: list[dict]    — [{value: str, label: str}]
        guarantee: str       — guarantee text (e.g. "七天无理由 · 工厂直发")
        testimonial: dict    — {quote: str, author: str}
    """

    name = "trust-signal"

    def css(self) -> str:
        return """
        .ts-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:radial-gradient(ellipse at 50% 30%,#1a1a2e 0%,#0a0a14 70%);
        }
        .ts-title {
            position:absolute;top:200px;left:60px;right:60px;
            color:#fff;font-size:48px;font-weight:900;text-align:center;
        }
        .ts-stat-card {
            position:absolute;width:300px;text-align:center;
        }
        .ts-stat-value {
            font-size:68px;font-weight:900;
            color:var(--brand-primary, #e8b45a);
            line-height:1.1;
        }
        .ts-stat-label {
            font-size:28px;color:#999;margin-top:8px;
        }
        .ts-guarantee {
            position:absolute;z-index:6;
            background:rgba(0,0,0,0.75);color:#fff;
            padding:24px 40px;border-radius:18px;
            border:1px solid var(--brand-primary, #e8b45a);
            text-align:center;font-size:32px;font-weight:600;
        }
        .ts-testimonial {
            position:absolute;z-index:6;text-align:center;
        }
        .ts-quote {
            color:#fff;font-size:36px;font-weight:600;line-height:1.5;
            font-style:italic;
        }
        .ts-author {
            color:var(--brand-primary, #e8b45a);font-size:28px;margin-top:12px;
        }
        """

    def html(self) -> str:
        c = self.config
        title = c.get("title", "为什么选择我们")

        stats_html = ""
        stats = c.get("stats", [])
        positions = [(80, 600), (390, 600), (700, 600)]  # 3-column layout
        for i, stat in enumerate(stats):
            if i < len(positions):
                left, top = positions[i]
                stats_html += f"""
                <div class="ts-stat-card" id="tsStat{i}" style="left:{left}px;top:{top}px;">
                    <div class="ts-stat-value">{stat.get('value','')}</div>
                    <div class="ts-stat-label">{stat.get('label','')}</div>
                </div>
                """

        guarantee_html = ""
        if c.get("guarantee"):
            guarantee_html = f"""
            <div class="ts-guarantee" id="tsGuarantee" style="bottom:500px;left:50%;transform:translateX(-50%);">
                ✓ {c['guarantee']}
            </div>
            """

        testimonial_html = ""
        tm = c.get("testimonial")
        if tm:
            testimonial_html = f"""
            <div class="ts-testimonial" id="tsTestimonial" style="bottom:250px;left:80px;right:80px;">
                <div class="ts-quote">"{tm.get('quote','')}"</div>
                <div class="ts-author">—— {tm.get('author','')}</div>
            </div>
            """

        return f"""
        <div class="ts-bg"></div>
        <div class="ts-title" id="tsTitle">{title}</div>
        {stats_html}
        {guarantee_html}
        {testimonial_html}
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Trust signal @ {t:.1f}s
        tl.from("#tsTitle",{{opacity:0,y:-20,duration:0.5,ease:"power3.out"}},{t+0.2});
        """
        for i in range(len(self.config.get("stats", []))):
            lines += f'tl.from("#tsStat{i}",{{opacity:0,y:30,scale:0.8,duration:0.45,ease:"back.out(1.5)"}},{t+0.7+i*0.35});\n'
        if self.config.get("guarantee"):
            lines += f'tl.from("#tsGuarantee",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+2.0});\n'
        if self.config.get("testimonial"):
            lines += f'tl.from("#tsTestimonial",{{opacity:0,duration:0.6,ease:"power3.out"}},{t+2.6});\n'
        return lines


@_register
class CTAOutroComponent(Component):
    """Call-to-action end card — brand logo + save prompt + follow/like/comment CTAs.

    Visual arc: logo ring scales in → brand name fades up → save CTA pops →
    follow/share/comment prompts stagger in → teaser for next video.

    Config keys:
        brand_name: str      — brand/channel name
        brand_subtitle: str  — tagline (e.g. "每天一个电商拍摄技巧")
        save_text: str       — save CTA (e.g. "截图保存拍摄方案")
        ctas: list[str]      — follow/like/comment prompts
        teaser: str          — next video teaser
        brand_logo: str      — logo character or image path
    """

    name = "cta-outro"

    def css(self) -> str:
        return """
        .cta-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:radial-gradient(ellipse at 50% 35%,#1a1a2e 0%,#0a0a14 70%);
        }
        .cta-logo-ring-outer {
            position:absolute;border-radius:50%;
            border:2px solid rgba(255,255,255,0.06);
        }
        .cta-logo-inner {
            position:absolute;border-radius:50%;
            background:radial-gradient(circle,var(--brand-primary, rgba(232,180,90,0.15)) 0%,rgba(232,180,90,0.03) 70%);
            border:2px solid var(--brand-primary, rgba(232,180,90,0.3));
            display:flex;align-items:center;justify-content:center;
            color:var(--brand-primary, #e8b45a);font-size:80px;font-weight:900;
        }
        .cta-brand-name {
            position:absolute;color:#fff;font-size:58px;font-weight:900;
            text-align:center;letter-spacing:0.04em;
        }
        .cta-brand-sub {
            position:absolute;color:var(--brand-primary, #e8b45a);
            font-size:32px;font-weight:600;text-align:center;
        }
        .cta-save-btn {
            position:absolute;text-align:center;
        }
        .cta-save-inner {
            display:inline-block;background:var(--brand-primary, #e8b45a);
            color:#1a1a14;font-size:36px;font-weight:700;
            padding:18px 44px;border-radius:16px;
            box-shadow:0 8px 36px rgba(232,180,90,0.35);
        }
        .cta-action-row {
            position:absolute;display:flex;gap:80px;justify-content:center;
            color:#fff;font-size:30px;font-weight:600;
        }
        .cta-action-item {
            display:flex;flex-direction:column;align-items:center;gap:12px;
        }
        .cta-action-icon {
            width:72px;height:72px;border-radius:50%;
            background:rgba(255,255,255,0.06);
            display:flex;align-items:center;justify-content:center;
            font-size:34px;
        }
        .cta-teaser {
            position:absolute;color:#666;font-size:28px;text-align:center;
        }
        """

    def html(self) -> str:
        c = self.config
        brand = c.get("brand_name", c.get("title", "品牌名"))
        brand_sub = c.get("brand_subtitle", "关注我，每天一个电商拍摄技巧")
        save_text = c.get("save_text", "截图保存拍摄方案")
        logo_char = c.get("brand_logo", brand[0] if brand else "品")
        teaser = c.get("teaser", "")

        ctas = c.get("ctas", ["关注", "点赞", "评论"])
        cta_icons = {"关注": "+", "点赞": "♥", "评论": "💬", "转发": "↗", "收藏": "★"}
        cta_html = ""
        for action in ctas:
            icon = cta_icons.get(action, "•")
            cta_html += f'<div class="cta-action-item"><div class="cta-action-icon">{icon}</div><span>{action}</span></div>\n'

        teaser_html = ""
        if teaser:
            teaser_html = f'<div class="cta-teaser" id="ctaTeaser" style="bottom:130px;left:80px;right:80px;">{teaser}</div>'

        return f"""
        <div class="cta-bg"></div>
        <div class="cta-logo-ring-outer" id="ctaRing" style="top:380px;left:50%;margin-left:-160px;width:320px;height:320px;"></div>
        <div class="cta-logo-inner" id="ctaLogo" style="top:400px;left:50%;margin-left:-140px;width:280px;height:280px;">{logo_char}</div>
        <div class="cta-brand-name" id="ctaBrand" style="top:730px;left:80px;right:80px;">{brand}</div>
        <div class="cta-brand-sub" id="ctaSub" style="top:840px;left:80px;right:80px;">{brand_sub}</div>
        <div class="cta-save-btn" id="ctaSave" style="top:980px;left:50%;transform:translateX(-50%);">
            <div class="cta-save-inner">📸 {save_text}</div>
        </div>
        <div class="cta-action-row" id="ctaActions" style="top:1150px;left:80px;right:80px;">
            {cta_html}
        </div>
        {teaser_html}
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // CTA outro @ {t:.1f}s
        tl.from("#ctaRing",{{opacity:0,scale:0.3,duration:0.7,ease:"power3.out"}},{t+0.3});
        tl.to("#ctaRing",{{scale:1.1,opacity:0.4,duration:4,ease:"none"}},{t+1.0});
        tl.from("#ctaLogo",{{opacity:0,scale:0.3,duration:0.7,ease:"back.out(2)"}},{t+0.4});
        tl.to("#ctaLogo",{{boxShadow:"0 0 80px rgba(232,180,90,0.3)",duration:1.2,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+1.1});
        tl.from("#ctaBrand",{{opacity:0,y:30,duration:0.6,ease:"power3.out"}},{t+1.3});
        tl.from("#ctaSub",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+1.9});
        tl.from("#ctaSave",{{opacity:0,scale:0.6,duration:0.55,ease:"back.out(2)"}},{t+2.4});
        tl.to("#ctaSave",{{scale:1.04,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+3.0});
        tl.from("#ctaActions",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+3.4});
        """
        if self.config.get("teaser"):
            lines += f'tl.from("#ctaTeaser",{{opacity:0,y:10,duration:0.5,ease:"power3.out"}},{t+4.0});\n'
        return lines

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        return [
            SFXTrigger("whoosh_02", t + 0.3, 0.6),
            SFXTrigger("ding_01", t + 2.4, 0.8),
        ]

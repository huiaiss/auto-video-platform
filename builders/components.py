"""Reusable component library for HyperFrames HTML compositions.

Each component knows how to generate its:
- HTML structure (with configurable placeholders)
- CSS styles (scoped to the component)
- GSAP animation code (with configurable timing hooks)
- SFX triggers (sound effect cues at key animation moments)
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Base Component protocol
# ---------------------------------------------------------------------------

@dataclass
class SFXTrigger:
    """A sound effect cue tied to an animation moment."""
    sfx_id: str           # e.g. "ding_01", "whoosh_02"
    at_time: float        # absolute timeline time (seconds)
    volume: float = 0.8   # 0.0–1.0


@dataclass
class SubtitleLine:
    """A line of subtitle text with optional animation hints."""
    text: str                    # full line text
    start: float                 # absolute start time
    end: float                   # absolute end time
    mode: str = "fade"           # "fade" | "word_pop" | "char_pop"
    keywords: list[str] = field(default_factory=list)   # words to highlight


class Component:
    """Base class for a reusable composition component.

    Subclasses override:
    - html() → str:           return the HTML block
    - css() → str:            return scoped CSS rules (or "" if none)
    - gsap() → str:           return GSAP JS code (or "" if none)
    - sfx() → list[SFXTrigger]: return SFX cues
    - subtitles() → list[SubtitleLine]: return subtitle lines with timing
    """

    name: str = "base"
    style: str = "ai_flaw_detect"

    def __init__(self, config: dict, start: float, duration: float):
        self.config = config
        self.start = start
        self.duration = duration
        self.end = start + duration

    @property
    def css_class(self) -> str:
        return f"comp-{self.name}"

    def html(self) -> str:
        return ""

    def css(self) -> str:
        return ""

    def gsap(self) -> str:
        return ""

    def sfx(self) -> list[SFXTrigger]:
        return []

    def subtitles(self) -> list[SubtitleLine]:
        return []

    def render(self) -> str:
        """Return the full HTML block for this component (used by assembler)."""
        return self.html()


# ---------------------------------------------------------------------------
# Component Registry
# ---------------------------------------------------------------------------

COMPONENT_REGISTRY: dict[str, type[Component]] = {}


def _register(cls: type[Component]) -> type[Component]:
    COMPONENT_REGISTRY[cls.name] = cls
    return cls


def load_components():
    """Ensure all components are imported and registered."""
    # Import side effects register all component classes
    pass


# ---------------------------------------------------------------------------
# Component implementations
# ---------------------------------------------------------------------------

@_register
class SocialFrameComponent(Component):
    """S1: Social media frame (朋友圈) — pseudo-realism hook opener."""

    name = "social-frame"

    def css(self) -> str:
        return """
        .sm-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:linear-gradient(180deg,#1a1a1a 0%,#111 40%,#0d0d0d 100%);
        }
        .sm-statusbar {
            position:absolute;top:0;left:0;width:1080px;height:90px;
            display:flex;justify-content:space-between;align-items:center;
            padding:30px 50px;color:#fff;font-size:26px;font-weight:600;
            background:rgba(0,0,0,0.3);
        }
        .sm-header {
            position:absolute;top:90px;left:0;width:1080px;height:80px;
            display:flex;align-items:center;padding:0 50px;
            border-bottom:1px solid rgba(255,255,255,0.06);
        }
        .sm-header-title{color:#fff;font-size:34px;font-weight:700;flex:1;text-align:center;}
        .sm-avatar{width:84px;height:84px;border-radius:50%;
            background:linear-gradient(135deg,#f5a623,#f76b1c);
            display:flex;align-items:center;justify-content:center;
            color:#fff;font-size:36px;font-weight:900;}
        .sm-username{color:#ecbe6b;font-size:32px;font-weight:700;}
        .sm-post-text{color:#ddd;font-size:30px;line-height:1.6;}
        .sm-photo-wrap{width:100%;max-height:820px;border-radius:12px;overflow:hidden;position:relative;}
        .sm-photo-wrap img{width:100%;display:block;max-height:820px;object-fit:cover;}
        .sm-likes-heart{color:#e74c3c;}
        .sm-comment{padding:10px 0;font-size:26px;line-height:1.5;}
        .sm-comment-name{color:#5b7fba;}
        """

    def html(self) -> str:
        c = self.config
        username = c.get("username", "用户")
        avatar_letter = c.get("avatar_letter", username[0])
        post_text = c.get("post_text", "聚会太开心啦")
        post_time = c.get("post_time", "3小时前")
        img_src = c.get("img_src", c.get("asset_path", ""))
        likes = c.get("likes", "128")
        comments = c.get("comments", [
            ("小美", "好美啊！在哪里拍的？"),
            ("大明", "下次带我一起！"),
            (f"{username} 回复 小美", "就在城西那家新开的店~"),
        ])

        comment_html = "\n".join(
            f'<div class="sm-comment"><span class="sm-comment-name">{name}</span>{text}</div>'
            for name, text in comments
        )

        return f"""
        <div class="sm-bg" id="smBg"></div>
        <div class="sm-statusbar" id="smStatus">
            <span>9:41</span>
            <span style="font-size:22px;color:#888;">WiFi · 满电</span>
        </div>
        <div class="sm-header" id="smHdr">
            <span style="color:#fff;font-size:24px;">← 返回</span>
            <span class="sm-header-title">朋友圈</span>
            <span style="color:#aaa;font-size:24px;">📷</span>
        </div>
        <div id="smPost" style="position:absolute;top:180px;left:30px;right:30px;bottom:0;">
            <div style="display:flex;align-items:center;gap:18px;padding:10px 0 20px;" id="smUser">
                <div class="sm-avatar">{avatar_letter}</div>
                <span class="sm-username">{username}</span>
                <span style="color:#666;font-size:22px;margin-left:auto;">{post_time}</span>
            </div>
            <div class="sm-post-text" id="smText">{post_text}</div>
            <div class="sm-photo-wrap" id="smPhoto">
                <img src="{img_src}" />
            </div>
            <div style="display:flex;gap:50px;padding:24px 0;" id="smActions">
                <div style="display:flex;align-items:center;gap:10px;color:#fff;font-size:28px;">
                    <span style="width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;">❤</span> 赞
                </div>
                <div style="display:flex;align-items:center;gap:10px;color:#fff;font-size:28px;">
                    <span style="width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:center;">💬</span> 评论
                </div>
            </div>
            <div style="padding:8px 0;color:#888;font-size:26px;" id="smLikes">
                <span class="sm-likes-heart">❤</span> {likes}人赞了
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.05);padding:18px 0;" id="smComments">
                {comment_html}
            </div>
        </div>
        """

    def gsap(self) -> str:
        t = self.start
        return f"""
        // Social frame build-up
        tl.set("#smBg",{{opacity:0}},{t});
        tl.to("#smBg",{{opacity:1,duration:0.4,ease:"power3.out"}},{t+0.1});
        tl.from("#smStatus",{{opacity:0,y:-30,duration:0.35,ease:"power3.out"}},{t+0.2});
        tl.from("#smHdr",{{opacity:0,y:-20,duration:0.35,ease:"power3.out"}},{t+0.35});
        tl.from("#smUser",{{opacity:0,x:-30,duration:0.45,ease:"power3.out"}},{t+0.6});
        tl.from("#smText",{{opacity:0,y:10,duration:0.4,ease:"power3.out"}},{t+0.9});
        tl.from("#smPhoto",{{opacity:0,scale:0.96,duration:0.6,ease:"power3.out"}},{t+1.1});
        tl.from("#smActions",{{opacity:0,duration:0.4,ease:"power3.out"}},{t+1.5});
        tl.from("#smLikes",{{opacity:0,duration:0.4,ease:"power3.out"}},{t+1.8});
        tl.to("#smLikes",{{scale:1.04,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+2.2});
        tl.from("#smComments>*:nth-child(1)",{{opacity:0,x:-20,duration:0.35,ease:"power3.out"}},{t+2.3});
        tl.from("#smComments>*:nth-child(2)",{{opacity:0,x:-20,duration:0.35,ease:"power3.out"}},{t+2.7});
        tl.from("#smComments>*:nth-child(3)",{{opacity:0,x:-20,duration:0.35,ease:"power3.out"}},{t+3.1});
        tl.to("#smPhoto img",{{scale:1.04,duration:6,ease:"none"}},{t});
        """


@_register
class GlitchTransitionComponent(Component):
    """Glitch/RGB-split transition from social frame to analysis mode."""

    name = "glitch-transition"

    def css(self) -> str:
        return """
        .glitch-r{position:absolute;top:0;left:0;width:1080px;height:1920px;background:#ff0040;mix-blend-mode:screen;opacity:0;z-index:42;}
        .glitch-g{position:absolute;top:0;left:0;width:1080px;height:1920px;background:#00ff40;mix-blend-mode:screen;opacity:0;z-index:42;}
        .glitch-b{position:absolute;top:0;left:0;width:1080px;height:1920px;background:#0040ff;mix-blend-mode:screen;opacity:0;z-index:42;}
        .glitch-slice{position:absolute;left:0;width:1080px;height:200px;z-index:43;background:rgba(255,255,255,0.3);opacity:0;}
        .glitch-vcr{position:absolute;top:0;left:0;width:1080px;height:1920px;z-index:44;
            background:repeating-linear-gradient(0deg,transparent,transparent 4px,rgba(0,0,0,0.03) 4px,rgba(0,0,0,0.03) 6px);
            opacity:0;pointer-events:none;}
        """

    def html(self) -> str:
        return """
        <div class="glitch-r" id="glR"></div>
        <div class="glitch-g" id="glG"></div>
        <div class="glitch-b" id="glB"></div>
        <div class="glitch-slice" id="glS1" style="top:300px;"></div>
        <div class="glitch-slice" id="glS2" style="top:900px;height:160px;"></div>
        <div class="glitch-slice" id="glS3" style="top:1500px;height:120px;"></div>
        <div class="glitch-vcr" id="glVcr"></div>
        """

    def gsap(self) -> str:
        t = self.start
        # Glitch hint → build-up → BIG GLITCH → clear
        return f"""
        // Subtle glitch hint
        tl.to("#glVcr",{{opacity:0.25,duration:0.08}},{t+0});
        tl.to("#glVcr",{{opacity:0,duration:0.06}},{t+0.08});
        tl.to("#glR",{{opacity:0.12,duration:0.05}},{t+0.15});
        tl.to("#glR",{{opacity:0,duration:0.04}},{t+0.2});

        // Stronger glitch
        tl.to("#glVcr",{{opacity:0.5,duration:0.06}},{t+0.6});
        tl.to("#glVcr",{{opacity:0,duration:0.04}},{t+0.66});
        tl.to("#glS1",{{opacity:0.6,duration:0.04}},{t+0.62});
        tl.to("#glS1",{{opacity:0,duration:0.03}},{t+0.66});
        tl.to("#glR",{{opacity:0.2,duration:0.04}},{t+0.64});
        tl.to("#glB",{{opacity:0.2,duration:0.04}},{t+0.65});
        tl.to("#glR",{{opacity:0,duration:0.03}},{t+0.68});
        tl.to("#glB",{{opacity:0,duration:0.03}},{t+0.69});

        // THE BIG GLITCH
        tl.to("#glVcr",{{opacity:0.7,duration:0.08}},{t+1.1});
        tl.to("#glR",{{opacity:0.35,duration:0.06}},{t+1.12});
        tl.to("#glG",{{opacity:0.2,duration:0.05}},{t+1.14});
        tl.to("#glB",{{opacity:0.3,duration:0.06}},{t+1.13});
        tl.to("#glS1",{{opacity:0.7,duration:0.06}},{t+1.16});
        tl.to("#glS2",{{opacity:0.55,duration:0.05}},{t+1.18});
        tl.to("#glS3",{{opacity:0.6,duration:0.05}},{t+1.15});

        // Clear
        tl.to("#glVcr",{{opacity:0,duration:0.06}},{t+1.3});
        tl.to("#glR",{{opacity:0,duration:0.05}},{t+1.28});
        tl.to("#glG",{{opacity:0,duration:0.05}},{t+1.3});
        tl.to("#glB",{{opacity:0,duration:0.05}},{t+1.29});
        tl.to("#glS1",{{opacity:0,duration:0.04}},{t+1.26});
        tl.to("#glS2",{{opacity:0,duration:0.04}},{t+1.28});
        tl.to("#glS3",{{opacity:0,duration:0.04}},{t+1.27});

        // Hide social frame
        tl.to("#smPost",{{opacity:0,duration:0.25}},{t+1.35});
        tl.to("#smBg",{{opacity:0,duration:0.3}},{t+1.4});
        tl.to("#smStatus",{{opacity:0,duration:0.2}},{t+1.3});
        tl.to("#smHdr",{{opacity:0,duration:0.2}},{t+1.3});
        """

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        return [
            SFXTrigger("glitch_01", t + 0.62, 0.7),
            SFXTrigger("glitch_02", t + 1.12, 1.0),
        ]


@_register
class RevealTextComponent(Component):
    """Post-glitch reveal: dark bg + photo + "它不是真人拍的。是AI生成的。" """

    name = "reveal-text"

    def html(self) -> str:
        reveal = self.config.get("reveal_text", "它不是真人拍的。<br/>是AI生成的。")
        anticipation = self.config.get("anticipation_text", "来，我放大三个细节给你看 ↓")
        img_src = self.config.get("img_src", self.config.get("asset_path", ""))
        return f"""
        <div style="position:absolute;top:0;left:0;width:1080px;height:1920px;background:#06060b;z-index:1;opacity:0;" id="s1Dark"></div>
        <img src="{img_src}" style="position:absolute;width:1080px;height:1920px;object-fit:cover;z-index:2;opacity:0;" id="img1" />
        <div style="position:absolute;top:680px;left:80px;right:80px;z-index:50;color:#ff1744;font-size:64px;font-weight:900;text-align:center;text-shadow:0 0 60px rgba(255,23,68,0.6);opacity:0;" id="revealTxt">{reveal}</div>
        <div style="position:absolute;top:800px;left:120px;right:120px;z-index:50;color:#fff;font-size:42px;font-weight:700;text-align:center;opacity:0;" id="anticTxt">{anticipation}</div>
        <div style="position:absolute;bottom:0;left:0;width:1080px;height:500px;background:linear-gradient(to top,rgba(6,6,11,0.95) 0%,rgba(6,6,11,0.5) 50%,transparent 100%);z-index:5;"></div>
        <div style="position:absolute;top:0;left:0;width:1080px;height:200px;background:linear-gradient(to bottom,rgba(6,6,11,0.7) 0%,transparent 100%);z-index:5;"></div>
        """

    def gsap(self) -> str:
        t = self.start
        return f"""
        tl.set("#s1Dark",{{opacity:0}},{t});
        tl.to("#s1Dark",{{opacity:1,duration:0.5,ease:"power3.out"}},{t+0.1});
        tl.set("#img1",{{opacity:0,scale:1}},{t+0.1});
        tl.to("#img1",{{opacity:0.75,duration:0.6,ease:"power3.out"}},{t+0.2});
        tl.from("#revealTxt",{{opacity:0,scale:0.8,duration:0.5,ease:"back.out(2)"}},{t+0.5});
        tl.to("#revealTxt",{{scale:1.04,duration:0.3,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+1.0});
        tl.from("#anticTxt",{{opacity:0,y:30,duration:0.5,ease:"power3.out"}},{t+1.7});
        """

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        return [
            SFXTrigger("impact_01", t + 0.5, 0.9),
            SFXTrigger("ding_01", t + 1.0, 0.6),
        ]


@_register
class ZoomAnalyzeComponent(Component):
    """S2-S4: Zoom into specific area + neon circle marker + keyword tag + data badge.

    Config keys:
        label: str            — scene label (e.g. "① 先看脸")
        img_id: str           — unique image element id
        img_src: str          — source image path
        zoom_origin_x: int    — transform-origin x
        zoom_origin_y: int    — transform-origin y
        zoom_scale: float     — max zoom (e.g. 2.6)
        keyword_text: str     — big red/amber tag text
        keyword_color: str    — "#ff1744" or "#ff9100"
        markers: list[dict]   — neon circle markers [{x,y,w,h,id}]
        data_badge: dict      — {text, sub_text, position}
        reference_lines: list[dict] — [{type, top, id}]
    """

    name = "zoom-analyze"

    def css(self) -> str:
        return """
        .neon-circle{position:absolute;border-radius:50%;z-index:12;pointer-events:none;
            border:5px solid #ff1744;
            box-shadow:0 0 50px rgba(255,23,68,0.8),0 0 90px rgba(255,23,68,0.35);}
        .neon-circle-inner{position:absolute;border-radius:50%;
            border:2px dashed rgba(255,23,68,0.45);}
        .keyword-tag{position:absolute;z-index:13;pointer-events:none;
            background:#ff1744;color:#fff;
            font-size:34px;font-weight:900;padding:12px 30px;border-radius:14px;
            box-shadow:0 0 50px rgba(255,23,68,0.6),0 8px 24px rgba(0,0,0,0.5);}
        .deviation-tag{position:absolute;z-index:14;pointer-events:none;
            background:rgba(0,0,0,0.9);color:#ff1744;
            font-size:28px;font-weight:700;padding:10px 22px;border-radius:12px;
            border:1px solid rgba(255,23,68,0.5);}
        .deviation-big{font-size:54px;font-weight:900;display:block;line-height:1.1;}
        .meas-ref-line{position:absolute;z-index:13;pointer-events:none;
            height:3px;background:#00e676;
            box-shadow:0 0 18px rgba(0,230,118,0.5);}
        .meas-deviation-line{position:absolute;z-index:13;pointer-events:none;
            height:4px;background:#ff1744;
            box-shadow:0 0 26px rgba(255,23,68,0.6);}
        .joint-straight-line{position:absolute;z-index:13;pointer-events:none;
            height:5px;background:#ff9100;
            box-shadow:0 0 28px rgba(255,145,0,0.7);
            transform-origin:left center;}
        .count-badge{position:absolute;z-index:14;pointer-events:none;
            width:80px;height:80px;border-radius:50%;
            background:#ff1744;color:#fff;
            font-size:42px;font-weight:900;
            display:flex;align-items:center;justify-content:center;
            box-shadow:0 0 40px rgba(255,23,68,0.7);}
        """

    def html(self) -> str:
        c = self.config
        img_id = c.get("img_id", f"img_z{int(self.start)}")
        img_src = c.get("img_src", c.get("asset_path", ""))
        ox = c.get("zoom_origin_x", 540)
        oy = c.get("zoom_origin_y", 960)
        label = c.get("label", "")
        keyword = c.get("keyword_text", "")
        kw_color = c.get("keyword_color", "#ff1744")
        kw_top = c.get("keyword_top", 760)
        kw_left = c.get("keyword_left", 100)
        kw_id = c.get("keyword_id", f"kw{int(self.start)}")
        lbl_id = c.get("label_id", f"lbl{int(self.start)}")

        markers_html = ""
        for m in c.get("markers", []):
            mid = m["id"]
            markers_html += f"""
            <div class="neon-circle" id="{mid}" style="width:{m['w']}px;height:{m['h']}px;top:{m['y']-m['h']//2}px;left:{m['x']-m['w']//2}px;{m.get('style','')}"></div>
            """

        data_html = ""
        db = c.get("data_badge")
        if db:
            dt_id = c.get("data_id", f"dv{int(self.start)}")
            data_html = f"""
            <div class="deviation-tag" id="{dt_id}" style="top:{db.get('top',700)}px;right:{db.get('right',70)}px;">
                <span class="deviation-big">{db.get('big','')}</span>{db.get('sub','')}
            </div>
            """

        ref_html = ""
        for r in c.get("reference_lines", []):
            rid = r["id"]
            cls = "meas-ref-line" if r.get("type") == "ref" else "meas-deviation-line" if r.get("type") == "deviation" else "joint-straight-line"
            ref_html += f'<div class="{cls}" id="{rid}" style="top:{r["top"]}px;left:{r.get("left",0)}px;width:0;"></div>\n'

        count_html = ""
        cb = c.get("count_badge")
        if cb:
            count_html = f"""
            <div class="count-badge" id="{c.get('count_id','cb3')}" style="top:{cb.get('top',1020)}px;right:{cb.get('right',80)}px;">{cb.get('value','4')}</div>
            """

        return f"""
        <div style="width:1080px;height:1920px;overflow:hidden;position:absolute;" data-layout-allow-overflow>
            <img src="{img_src}" style="position:absolute;width:1080px;height:1920px;object-fit:cover;will-change:transform;transform-origin:{ox}px {oy}px;" id="{img_id}" />
        </div>
        <div style="position:absolute;bottom:0;left:0;width:1080px;height:700px;background:linear-gradient(to top,rgba(6,6,11,0.95),rgba(6,6,11,0.5),transparent);"></div>
        <div style="position:absolute;top:0;left:0;width:1080px;height:200px;background:linear-gradient(to bottom,rgba(6,6,11,0.7),transparent);"></div>
        {markers_html}
        <div class="keyword-tag" id="{kw_id}" style="top:{kw_top}px;left:{kw_left}px;background:{kw_color};">{keyword}</div>
        {data_html}
        {ref_html}
        {count_html}
        <div style="position:absolute;top:80px;left:60px;color:#00e676;font-size:26px;font-weight:700;letter-spacing:0.15em;z-index:11;background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.2);padding:8px 24px;border-radius:8px;" id="{lbl_id}">{label}</div>
        """

    def gsap(self) -> str:
        t = self.start
        c = self.config
        img_id = c.get("img_id", f"img_z{int(t)}")
        zoom_scale = c.get("zoom_scale", 2.6)
        kw_id = c.get("keyword_id", f"kw{int(t)}")
        lbl_id = c.get("label_id", f"lbl{int(t)}")

        lines = [f"""
        // Zoom-analyze scene @ {t:.3f}s
        tl.set("#{img_id}",{{scale:1}},{t});
        tl.to("#{img_id}",{{scale:{zoom_scale},duration:1.5,ease:"power3.inOut"}},{t});
        tl.from("#{lbl_id}",{{opacity:0,x:-30,duration:0.4,ease:"power3.out"}},{t+0.6});
        """]

        # Markers
        for i, m in enumerate(c.get("markers", [])):
            mid = m["id"]
            delay = m.get("delay", 1.5 + i * 0.8)
            lines.append(f"""
        tl.from("#{mid}",{{opacity:0,scale:0.2,duration:0.5,ease:"back.out(2)"}},{t+delay});
        tl.to("#{mid}",{{scale:1.12,duration:0.55,repeat:3,yoyo:true,ease:"sine.inOut"}},{t+delay+0.5});
        """)

        # Keyword tag
        kw_delay = c.get("keyword_delay", 1.5)
        lines.append(f"""
        tl.from("#{kw_id}",{{opacity:0,scale:0.3,y:-20,duration:0.5,ease:"back.out(2)"}},{t+kw_delay});
        tl.to("#{kw_id}",{{y:-8,duration:0.8,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+kw_delay+0.5});
        """)

        # Reference lines
        for r in c.get("reference_lines", []):
            rid = r["id"]
            w = r.get("width", 1080)
            d = r.get("delay", 2.5)
            lines.append(f'tl.to("#{rid}",{{width:{w},duration:0.8,ease:"power3.out"}},{t+d});\n')

        # Data badge
        db = c.get("data_badge")
        if db:
            dt_id = c.get("data_id", f"dv{int(t)}")
            db_delay = c.get("data_delay", 3.0)
            lines.append(f'tl.from("#{dt_id}",{{opacity:0,x:40,duration:0.45,ease:"power3.out"}},{t+db_delay});\n')

        # Count badge
        cb = c.get("count_badge")
        if cb:
            cid = c.get("count_id", "cb3")
            cb_delay = c.get("count_delay", 4.0)
            lines.append(f"""
        tl.from("#{cid}",{{opacity:0,scale:0,duration:0.5,ease:"back.out(2)"}},{t+cb_delay});
        tl.to("#{cid}",{{scale:1.18,duration:0.4,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+cb_delay+0.5});
        """)

        # Zoom-out (if configured)
        if c.get("zoom_out_at"):
            lines.append(f'tl.to("#{img_id}",{{scale:1.0,duration:0.9,ease:"power3.inOut"}},{c["zoom_out_at"]});\n')

        return "\n".join(lines)

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        triggers = []
        for i, m in enumerate(self.config.get("markers", [])):
            delay = m.get("delay", 1.5 + i * 0.8)
            triggers.append(SFXTrigger("ping_01", t + delay, 0.7))
        kw_delay = self.config.get("keyword_delay", 1.5)
        triggers.append(SFXTrigger("whoosh_01", t + kw_delay, 0.6))
        return triggers


@_register
class CompareSplitComponent(Component):
    """S5: Left-vs-right split screen comparison + checklist."""

    name = "compare-split"

    def css(self) -> str:
        return """
        .compare-wrap{position:absolute;top:160px;left:30px;right:30px;bottom:440px;display:flex;gap:12px;}
        .compare-half{flex:1;border-radius:16px;overflow:hidden;position:relative;border:2px solid rgba(255,255,255,0.06);}
        .compare-half img{width:100%;height:100%;object-fit:cover;}
        .compare-badge{position:absolute;top:12px;left:12px;padding:8px 22px;border-radius:22px;font-size:24px;font-weight:700;}
        .badge-ai{background:rgba(255,23,68,0.15);color:#ff1744;border:1px solid rgba(255,23,68,0.4);}
        .badge-real{background:rgba(0,230,118,0.12);color:#00e676;border:1px solid rgba(0,230,118,0.4);}
        .compare-divider{position:absolute;top:50%;left:50%;margin-left:-44px;margin-top:-44px;width:88px;height:88px;border-radius:50%;
            background:rgba(0,0,0,0.8);border:2px solid rgba(255,255,255,0.2);
            display:flex;align-items:center;justify-content:center;z-index:5;
            color:#fff;font-size:44px;font-weight:900;}
        .checklist-row{display:flex;justify-content:space-between;align-items:center;padding:10px 24px;border-radius:12px;background:rgba(0,0,0,0.55);}
        .checklist-label{color:#fff;font-size:32px;font-weight:600;}
        .checklist-fail{color:#ff1744;font-size:32px;font-weight:700;}
        .checklist-pass{color:#00e676;font-size:32px;font-weight:700;}
        """

    def html(self) -> str:
        c = self.config
        fallback_img = c.get("img_src", c.get("asset_path", ""))
        ai_img = c.get("ai_img", fallback_img or "assets/img2_group_photo.png")
        real_img = c.get("real_img", fallback_img or "assets/real_group_generated.png")
        checks = c.get("checks", [
            {"label": "脸对不对称", "fail": "✗ 歪了", "pass": "✓ 对称"},
            {"label": "手指分不分得开", "fail": "✗ 黏了", "pass": "✓ 分明"},
            {"label": "关节有没有弯", "fail": "✗ 直了", "pass": "✓ 弯曲"},
        ])
        summary = c.get("summary_text", "记住查三处：脸 · 手 · 关节")

        check_html = ""
        for i, ch in enumerate(checks):
            check_html += f"""
            <div class="checklist-row" id="chk{i+1}">
                <span class="checklist-label">{ch['label']}</span>
                <span class="checklist-fail">{ch['fail']}</span>
                <span class="checklist-pass" style="opacity:0;">{ch['pass']}</span>
            </div>
            """

        return f"""
        <div style="position:absolute;top:0;left:0;width:1080px;height:1920px;background:radial-gradient(ellipse at 50% 40%,#0d1b2a 0%,#06060b 70%);"></div>
        <div class="compare-wrap" id="cmpWrap">
            <div class="compare-half" id="cmpAI">
                <img src="{ai_img}" />
                <div class="compare-badge badge-ai">✗ AI生成</div>
            </div>
            <div class="compare-half" id="cmpReal">
                <img src="{real_img}" />
                <div class="compare-badge badge-real">✓ 真人照片</div>
            </div>
        </div>
        <div class="compare-divider" id="cmpDiv">VS</div>
        <div style="position:absolute;bottom:300px;left:30px;right:30px;display:flex;flex-direction:column;gap:10px;z-index:12;" id="chklist">
            {check_html}
        </div>
        <div style="position:absolute;bottom:0;left:0;width:1080px;height:380px;background:linear-gradient(to top,rgba(6,6,11,0.95),rgba(6,6,11,0.5),transparent);"></div>
        <div style="position:absolute;bottom:180px;left:60px;right:60px;z-index:10;text-align:center;" id="txt5">
            <div style="display:inline-block;background:rgba(0,0,0,0.78);border-radius:18px;padding:24px 44px;border:1px solid rgba(255,255,255,0.06);">
                <div style="color:#fff;font-size:50px;font-weight:700;line-height:1.5;text-shadow:0 2px 16px rgba(0,0,0,0.9);letter-spacing:0.03em;">{summary}</div>
            </div>
        </div>
        """

    def gsap(self) -> str:
        t = self.start
        n = len(self.config.get("checks", [1, 2, 3]))
        lines = [f"""
        // Compare split-scene @ {t:.3f}s
        tl.from("#cmpAI",{{opacity:0,x:-70,duration:0.65,ease:"power3.out"}},{t+0.3});
        tl.from("#cmpReal",{{opacity:0,x:70,duration:0.65,ease:"power3.out"}},{t+0.3});
        tl.from("#cmpDiv",{{opacity:0,scale:0.3,duration:0.45,ease:"back.out(2)"}},{t+0.7});
        tl.to("#cmpDiv",{{scale:1.06,duration:0.45,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+1.3});
        """]

        for i in range(n):
            lines.append(f'tl.from("#chk{i+1}",{{opacity:0,x:-40,duration:0.4,ease:"power3.out"}},{t+1.9+i*0.7});')
            lines.append(f'tl.to("#chk{i+1} .checklist-fail",{{scale:1.15,duration:0.3,repeat:1,yoyo:true,ease:"sine.inOut"}},{t+3.7+i*0.3});')

        lines.append(f'tl.from("#txt5",{{opacity:0,y:30,duration:0.5,ease:"power3.out"}},{t+1.3});')
        return "\n".join(lines)

    def sfx(self) -> list[SFXTrigger]:
        t = self.start
        n = len(self.config.get("checks", [1, 2, 3]))
        triggers = [SFXTrigger("whoosh_02", t + 0.3, 0.7)]
        for i in range(n):
            triggers.append(SFXTrigger("ding_02", t + 3.7 + i * 0.3, 0.5))
        return triggers


@_register
class TitleCardComponent(Component):
    """S7: Full-screen title card — dark bg + big centered text.

    Used for section transitions, emphasis, or "teaching moment" headers.
    Pure typography — no image dependency.
    """

    name = "title-card"

    def css(self) -> str:
        return """
        .tc-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:radial-gradient(ellipse at 50% 45%,#0d1b2a 0%,#06060b 70%);
        }
        .tc-accent-line {
            position:absolute;left:50%;transform:translateX(-50%);
            width:120px;height:4px;
            background:linear-gradient(90deg,transparent,var(--brand-primary,#00e676),transparent);
        }
        .tc-title {
            position:absolute;left:80px;right:80px;text-align:center;
            color:#fff;font-size:58px;font-weight:900;line-height:1.35;
            letter-spacing:0.03em;
        }
        .tc-subtitle {
            position:absolute;left:120px;right:120px;text-align:center;
            color:#999;font-size:32px;font-weight:500;line-height:1.5;
        }
        .tc-icon {
            position:absolute;text-align:center;font-size:80px;
        }
        """

    def html(self) -> str:
        c = self.config
        title = c.get("title_text", c.get("caption", "标题"))
        subtitle = c.get("subtitle_text", "")
        icon = c.get("icon", "🔍")

        subtitle_html = ""
        if subtitle:
            subtitle_html = (
                f'<div class="tc-subtitle" id="tcSub" '
                f'style="top:1050px;">{subtitle}</div>'
            )

        return f"""
        <div class="tc-bg"></div>
        <div class="tc-accent-line" id="tcLine" style="top:560px;"></div>
        <div class="tc-icon" id="tcIcon" style="top:620px;left:50%;margin-left:-50px;">{icon}</div>
        <div class="tc-title" id="tcTitle" style="top:760px;">{title}</div>
        {subtitle_html}
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Title card @ {t:.1f}s
        tl.from("#tcLine",{{opacity:0,scaleX:0,duration:0.5,ease:"power3.out"}},{t+0.2});
        tl.from("#tcIcon",{{opacity:0,scale:0.3,y:20,duration:0.5,ease:"back.out(2)"}},{t+0.4});
        tl.from("#tcTitle",{{opacity:0,y:30,duration:0.55,ease:"power3.out"}},{t+0.7});
        """
        if self.config.get("subtitle_text"):
            lines += f'tl.from("#tcSub",{{opacity:0,y:15,duration:0.45,ease:"power3.out"}},{t+1.2});\n'
        return lines


@_register
class DataCardComponent(Component):
    """S8: Big-number statistic card — "X% of AI images have this flaw".

    Pure data visualization — no image dependency.
    """

    name = "data-card"

    def css(self) -> str:
        return """
        .dc-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:#06060b;
        }
        .dc-big-number {
            position:absolute;text-align:center;
            color:var(--brand-primary,#00e676);font-size:160px;font-weight:900;
            line-height:1;letter-spacing:-0.02em;
            text-shadow:0 0 80px rgba(0,230,118,0.3);
        }
        .dc-label {
            position:absolute;text-align:center;
            color:#fff;font-size:44px;font-weight:700;line-height:1.4;
        }
        .dc-source {
            position:absolute;text-align:center;
            color:#666;font-size:26px;
        }
        """

    def html(self) -> str:
        c = self.config
        number = c.get("number", c.get("big_number", "70%"))
        label = c.get("label", c.get("caption", ""))
        source = c.get("source_text", "")

        source_html = ""
        if source:
            source_html = (
                f'<div class="dc-source" id="dcSource" '
                f'style="bottom:400px;left:80px;right:80px;">{source}</div>'
            )

        return f"""
        <div class="dc-bg"></div>
        <div class="dc-big-number" id="dcNum" style="top:580px;left:80px;right:80px;">{number}</div>
        <div class="dc-label" id="dcLabel" style="top:860px;left:100px;right:100px;">{label}</div>
        {source_html}
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Data card @ {t:.1f}s
        tl.from("#dcNum",{{opacity:0,scale:0.5,y:40,duration:0.7,ease:"back.out(2)"}},{t+0.2});
        tl.to("#dcNum",{{scale:1.05,duration:0.35,yoyo:true,repeat:1,ease:"sine.inOut"}},{t+1.0});
        tl.from("#dcLabel",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+1.4});
        """
        if self.config.get("source_text"):
            lines += f'tl.from("#dcSource",{{opacity:0,y:10,duration:0.45,ease:"power3.out"}},{t+2.0});\n'
        return lines


@_register
class ChecklistCardComponent(Component):
    """S9: Full-screen checklist — the "take a screenshot" moment.

    Shows 3-5 check items with pass/fail indicators.
    Pure typography + layout — no image dependency.
    """

    name = "checklist-card"

    def css(self) -> str:
        return """
        .cl-bg {
            position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:radial-gradient(ellipse at 50% 40%,#0d1b2a 0%,#06060b 70%);
        }
        .cl-header {
            position:absolute;left:80px;right:80px;text-align:center;
            color:var(--brand-primary,#00e676);font-size:28px;font-weight:700;
            letter-spacing:0.1em;
        }
        .cl-title {
            position:absolute;left:80px;right:80px;text-align:center;
            color:#fff;font-size:52px;font-weight:900;line-height:1.35;
        }
        .cl-item {
            position:absolute;left:120px;right:120px;
            display:flex;align-items:center;justify-content:space-between;
            padding:24px 36px;border-radius:16px;
            background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
        }
        .cl-item-label {
            color:#ddd;font-size:34px;font-weight:600;
        }
        .cl-item-result {
            font-size:30px;font-weight:700;
        }
        .cl-item-fail { color:#ff1744; }
        .cl-item-pass { color:#00e676; }
        .cl-footer {
            position:absolute;left:80px;right:80px;text-align:center;
            color:#888;font-size:28px;
        }
        """

    def html(self) -> str:
        c = self.config
        title = c.get("title_text", c.get("caption", "检查清单"))
        items = c.get("items", c.get("checks", [
            {"label": "第1项", "result": "✗", "is_pass": False},
            {"label": "第2项", "result": "✓", "is_pass": True},
            {"label": "第3项", "result": "✗", "is_pass": False},
        ]))
        footer = c.get("footer_text", "📸 截图保存，下次直接对照")

        items_html = ""
        for i, item in enumerate(items):
            result_class = "cl-item-pass" if item.get("is_pass") else "cl-item-fail"
            top = 720 + i * 130
            items_html += f"""
            <div class="cl-item" id="clItem{i}" style="top:{top}px;">
                <span class="cl-item-label">{item.get('label','?')}</span>
                <span class="cl-item-result {result_class}">{item.get('result','?')}</span>
            </div>"""

        return f"""
        <div class="cl-bg"></div>
        <div class="cl-header" id="clHdr" style="top:380px;">AI 照妖镜 · 检查清单</div>
        <div class="cl-title" id="clTitle" style="top:480px;">{title}</div>
        {items_html}
        <div class="cl-footer" id="clFooter" style="bottom:200px;">{footer}</div>
        """

    def gsap(self) -> str:
        t = self.start
        lines = f"""
        // Checklist card @ {t:.1f}s
        tl.from("#clHdr",{{opacity:0,y:-15,duration:0.4,ease:"power3.out"}},{t+0.2});
        tl.from("#clTitle",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+0.6});
        """
        n = len(self.config.get("items", self.config.get("checks", [])))
        for i in range(n):
            lines += (
                f'tl.from("#clItem{i}",{{opacity:0,x:-40,duration:0.4,ease:"power3.out"}},'
                f'{t+1.0+i*0.35});\n'
            )
        lines += f'tl.from("#clFooter",{{opacity:0,y:10,duration:0.5,ease:"power3.out"}},{t+1.0+n*0.35+0.5});\n'
        return lines


@_register
class OutroComponent(Component):
    """S6: End card — logo ring + title + CTA + teaser."""

    name = "outro"

    def html(self) -> str:
        c = self.config
        title = c.get("title", "AI照妖镜")
        subtitle = c.get("subtitle", "关注我，下次被骗的不是你")
        teaser = c.get("teaser", "下期：5个AI检测工具横评 →")
        logo_char = c.get("logo_char", "AI")
        checklist = c.get("checklist", "")
        tags = c.get("tags", "")

        checklist_html = ""
        if checklist:
            checklist_html = f"""
        <div id="ochk" style="position:absolute;top:1040px;left:80px;right:80px;text-align:center;color:#aaa;font-size:28px;line-height:1.6;opacity:0;">
            <div style="color:#888;font-size:22px;margin-bottom:8px;">📸 截图保存</div>
            {checklist.replace(chr(10), '<br/>')}
        </div>"""

        tags_html = ""
        if tags:
            tags_html = f"""
        <div id="otags" style="position:absolute;top:1220px;left:80px;right:80px;text-align:center;color:#666;font-size:24px;opacity:0;">{tags}</div>"""

        return f"""
        <div style="position:absolute;top:0;left:0;width:1080px;height:1920px;background:radial-gradient(ellipse at 50% 40%,#0d1b2a,#06060b 70%);"></div>
        <div style="position:absolute;top:400px;left:50%;margin-left:-150px;width:300px;height:300px;border-radius:50%;border:2px solid rgba(0,230,118,0.12);" id="oring"></div>
        <div style="position:absolute;top:420px;left:50%;margin-left:-130px;width:260px;height:260px;border-radius:50%;
            background:radial-gradient(circle,rgba(0,230,118,0.1) 0%,rgba(0,230,118,0.02) 70%);
            border:2px solid rgba(0,230,118,0.2);
            display:flex;align-items:center;justify-content:center;" id="ologo">
            <span style="color:#00e676;font-size:88px;font-weight:900;">{logo_char}</span>
        </div>
        <div id="otitle" style="position:absolute;top:740px;left:80px;right:80px;text-align:center;color:#fff;font-size:64px;font-weight:900;">{title}</div>
        <div id="osub" style="position:absolute;top:850px;left:80px;right:80px;text-align:center;color:#00e676;font-size:36px;font-weight:600;">{subtitle}</div>
        <div id="oteaser" style="position:absolute;top:960px;left:80px;right:80px;text-align:center;color:#888;font-size:30px;">{teaser}</div>
        {checklist_html}
        {tags_html}
        """

    def gsap(self) -> str:
        t = self.start
        c = self.config
        lines = f"""
        tl.from("#oring",{{opacity:0,scale:0.3,duration:0.68,ease:"power3.out"}},{t+0.3});
        tl.to("#oring",{{scale:1.08,opacity:0.5,duration:3.5,ease:"none"}},{t+0.98});
        tl.from("#ologo",{{opacity:0,scale:0.3,duration:0.7,ease:"back.out(2)"}},{t+0.4});
        tl.to("#ologo",{{boxShadow:"0 0 90px rgba(0,230,118,0.35)",duration:1,repeat:2,yoyo:true,ease:"sine.inOut"}},{t+1.1});
        tl.from("#otitle",{{opacity:0,y:30,duration:0.6,ease:"power3.out"}},{t+1.2});
        tl.from("#osub",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+1.8});
        tl.from("#oteaser",{{opacity:0,y:15,duration:0.5,ease:"power3.out"}},{t+2.7});
        """
        if c.get("checklist"):
            lines += f'tl.from("#ochk",{{opacity:0,y:20,duration:0.5,ease:"power3.out"}},{t+3.2});\n'
        if c.get("tags"):
            lines += f'tl.from("#otags",{{opacity:0,y:10,duration:0.5,ease:"power3.out"}},{t+3.8});\n'
        return lines


@_register
class ScanOverlayComponent(Component):
    """Global: scan line overlay visible during analysis scenes."""

    name = "scan-overlay"

    def css(self) -> str:
        return """
        .scan-overlay{position:absolute;top:0;left:0;width:1080px;height:1920px;
            background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,230,118,0.006) 2px,rgba(0,230,118,0.006) 4px);
            z-index:30;pointer-events:none;}
        .scan-line{position:absolute;left:0;width:1080px;height:2px;
            background:linear-gradient(90deg,transparent,rgba(0,230,118,0.12),transparent);
            z-index:31;pointer-events:none;}
        """

    def html(self) -> str:
        show_at = self.config.get("show_at", self.start)
        hide_at = self.config.get("hide_at", self.end)
        return f"""
        <div class="scan-overlay" id="scanOverlay"></div>
        <div class="scan-line" id="scanLine" style="top:0;"></div>
        """

    def gsap(self) -> str:
        show = self.config.get("show_at", self.start)
        hide = self.config.get("hide_at", self.end)
        return f"""
        tl.set("#scanOverlay",{{opacity:0}},0);
        tl.set("#scanLine",{{opacity:0}},0);
        tl.to("#scanOverlay",{{opacity:1,duration:0.4}},{show});
        tl.to("#scanLine",{{opacity:1,duration:0.4}},{show});
        tl.to("#scanOverlay",{{opacity:0,duration:0.3}},{hide});
        tl.to("#scanLine",{{opacity:0,duration:0.3}},{hide});
        tl.fromTo("#scanLine",{{top:"-2%"}},{{top:"102%",duration:{hide-show},ease:"none"}},{show});
        """


@_register
class ProgressBarComponent(Component):
    """Top progress bar showing video completion."""

    name = "progress-bar"

    def css(self) -> str:
        return """
        .progress-bar-wrap{position:absolute;top:0;left:0;width:1080px;height:4px;z-index:32;background:rgba(255,255,255,0.03);}
        .progress-bar-fill{height:100%;width:0%;background:linear-gradient(90deg,#00e676,#00c853);}
        .progress-bar-dot{position:absolute;top:0;width:3px;height:6px;background:rgba(255,23,68,0.5);}
        """

    def html(self) -> str:
        segments = self.config.get("segments", [])
        dots = ""
        for seg in segments:
            pct = (seg["start"] / seg["total"]) * 100
            dots += f'<div class="progress-bar-dot" style="left:{pct}%;"></div>\n'
        return f"""
        <div class="progress-bar-wrap"><div class="progress-bar-fill" id="progressFill"></div>{dots}</div>
        """

    def gsap(self) -> str:
        total = self.config.get("total_duration", 53)
        return f"""
        tl.to("#progressFill",{{width:"100%",duration:{total},ease:"none"}},0);
        """

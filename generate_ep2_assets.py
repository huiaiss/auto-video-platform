"""Generate Episode 2 assets — AI images with garbled text flaws.

Creates synthetic AI-fail images that simulate what an AI image generator
produces: photo-realistic overall but with garbled/nonsensical text.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output", "ep2_assets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920

def create_base_scene(bg_color, scene_type="street"):
    """Create a base scene image."""
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    # Add some visual noise/grain for realism
    noise = np.random.randint(0, 15, (H, W, 3), dtype=np.uint8)
    img_np = np.array(img) + noise
    img = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))

    # Add gradient sky
    for y in range(H // 3):
        r = int(80 + y / (H / 3) * 60)
        g = int(100 + y / (H / 3) * 80)
        b = int(140 + y / (H / 3) * 100)
        for x in range(W):
            img.putpixel((x, y), (r, g, b))

    draw = ImageDraw.Draw(img)

    # Ground/sidewalk
    draw.rectangle([(0, H * 2 // 3), (W, H)], fill=(60, 55, 50))
    draw.rectangle([(0, H * 2 // 3), (W, H * 2 // 3 + 20)], fill=(90, 85, 80))

    return img, draw


def add_garbled_text(draw, x, y, w, h, bg_color=None):
    """Add a text area with garbled/AI-fake text."""
    if bg_color:
        draw.rectangle([(x, y), (x + w, y + h)], fill=bg_color)

    # Generate garbled text — mix of real and fake Chinese characters
    real_chars = "店招餐馆超市商场广场中心"
    fake_chars = "囗囘囙囜囝回囟囡団囤囥囦囧囨囩囫囬囮囯困囱囲図"
    mixed_chars = "燚鑫淼垚壵瞾"

    try:
        font_large = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 48)
        font_small = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 32)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw a sign background
    draw.rectangle([(x - 10, y - 10), (x + w + 10, y + h + 10)],
                   fill=random.choice([(200, 50, 30), (30, 80, 180), (40, 40, 40), (220, 220, 220)]),
                   outline=(0, 0, 0), width=2)

    # Add garbled text lines
    colors = [(255, 255, 255), (255, 255, 200), (255, 240, 100)]
    for row in range(4):
        line = ""
        for _ in range(random.randint(2, 5)):
            line += random.choice(mixed_chars + real_chars + "     口口巳己已巳口")
        font = font_large if row == 0 else font_small
        color = random.choice(colors)
        try:
            draw.text((x, y + row * 50), line, fill=color,
                     font=font, stroke_width=1, stroke_fill=(0, 0, 0))
        except Exception:
            draw.text((x, y + row * 50), line[:10], fill=color)

    # Add some random strokes/smudges typical of AI text
    for _ in range(random.randint(3, 8)):
        sx = x + random.randint(0, w)
        sy = y + random.randint(0, h)
        draw.ellipse([(sx, sy), (sx + 6, sy + 6)],
                     fill=random.choice([(120, 80, 60), (180, 160, 140), (60, 60, 60)]))


def image1_store_sign():
    """A storefront with garbled Chinese sign."""
    print("Generating image 1: Store sign...")
    img, draw = create_base_scene((70, 60, 55))

    # Buildings in background
    draw.rectangle([(100, 200), (980, 1300)], fill=(90, 75, 65))
    draw.rectangle([(0, 300), (900, 1300)], fill=(80, 70, 60))

    # Windows
    for wx in range(200, 800, 150):
        for wy in range(500, 1000, 200):
            draw.rectangle([(wx, wy), (wx + 100, wy + 140)],
                          fill=(180, 200, 220), outline=(40, 40, 40), width=3)

    # The store front with garbled sign
    draw.rectangle([(240, 400), (840, 900)], fill=(50, 45, 40), outline=(30, 30, 30), width=4)

    # Big garbled sign
    sign_x, sign_y = 280, 440
    sign_w, sign_h = 520, 160
    draw.rectangle([(sign_x, sign_y), (sign_x + sign_w, sign_y + sign_h)],
                   fill=(180, 30, 20))
    add_garbled_text(draw, sign_x + 20, sign_y + 20, sign_w - 40, sign_h - 40,
                    bg_color=None)

    # Door
    draw.rectangle([(400, 700), (680, 1300)], fill=(40, 35, 30),
                   outline=(60, 50, 40), width=5)
    draw.ellipse([(640, 950), (670, 980)], fill=(180, 170, 60))

    # Small garbled text on door
    add_garbled_text(draw, 420, 750, 240, 100)

    # Street lamp with garbled poster
    draw.rectangle([(150, 300), (170, 1100)], fill=(60, 60, 65))
    draw.ellipse([(130, 260), (190, 320)], fill=(255, 240, 200))

    # Poster on lamp post
    draw.rectangle([(120, 500), (220, 700)], fill=(240, 235, 220),
                   outline=(100, 90, 80), width=2)
    add_garbled_text(draw, 130, 520, 80, 160)

    path = os.path.join(OUTPUT_DIR, "ep2_img1_store_sign.png")
    img.save(path, quality=95)
    print(f"  Saved: {path}")
    return path


def image2_tshirt_text():
    """Person wearing t-shirt with garbled text."""
    print("Generating image 2: T-shirt garbled text...")
    img, draw = create_base_scene((65, 60, 70))

    # Simple figure
    cx, cy = 540, 700
    # Head
    draw.ellipse([(cx - 80, cy - 350), (cx + 80, cy - 190)], fill=(210, 180, 150))
    # Hair
    draw.ellipse([(cx - 85, cy - 370), (cx + 85, cy - 240)], fill=(40, 30, 20))
    # Eyes
    draw.ellipse([(cx - 30, cy - 290), (cx - 10, cy - 270)], fill=(30, 30, 30))
    draw.ellipse([(cx + 10, cy - 290), (cx + 30, cy - 270)], fill=(30, 30, 30))
    # Mouth
    draw.arc([(cx - 15, cy - 230), (cx + 15, cy - 210)], 0, 180, fill=(130, 80, 70), width=3)

    # Body / T-shirt
    draw.polygon([(cx, cy - 170), (cx - 180, cy + 300), (cx + 180, cy + 300)],
                 fill=(30, 80, 160))

    # Garbled text on T-shirt
    tshirt_cx, tshirt_cy = cx, cy - 20
    for row_idx, text in enumerate(["夊夋夌夎", "爨癵爩", "灬灬灬", "爨癵驫"]):
        # Use PIL to draw garbled chars
        draw.rectangle([(tshirt_cx - 120, tshirt_cy + row_idx * 55),
                       (tshirt_cx + 120, tshirt_cy + row_idx * 55 + 50)],
                       fill=None)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 42)
            draw.text((tshirt_cx - 100, tshirt_cy + row_idx * 55), text,
                     fill=(255, 255, 255), font=font,
                     stroke_width=2, stroke_fill=(20, 60, 140))
        except Exception:
            pass

    # Add some smudges around the text (AI artifact)
    for _ in range(15):
        sx = tshirt_cx + random.randint(-130, 130)
        sy = tshirt_cy + random.randint(-20, 200)
        size = random.randint(3, 15)
        draw.ellipse([(sx, sy), (sx + size, sy + size)],
                     fill=(random.randint(20, 60), random.randint(60, 100), random.randint(140, 180)))

    # Arm
    draw.line([(cx - 180, cy - 50), (cx - 250, cy + 100)], fill=(210, 180, 150), width=40)
    draw.line([(cx + 180, cy - 50), (cx + 250, cy + 100)], fill=(210, 180, 150), width=40)

    path = os.path.join(OUTPUT_DIR, "ep2_img2_tshirt_text.png")
    img.save(path, quality=95)
    print(f"  Saved: {path}")
    return path


def image3_street_signs():
    """Street scene with multiple garbled signs."""
    print("Generating image 3: Street scene...")
    img, draw = create_base_scene((80, 85, 90))

    # Road
    draw.rectangle([(0, 1200), (W, H)], fill=(50, 48, 45))
    # Lane markings
    for lx in range(100, W, 200):
        draw.rectangle([(lx, 1400), (lx + 80, 1420)], fill=(220, 210, 100))

    # Buildings on both sides
    draw.rectangle([(0, 200), (350, 1200)], fill=(70, 65, 60))
    draw.rectangle([(730, 200), (1080, 1200)], fill=(85, 75, 65))

    # Traffic sign post
    draw.rectangle([(500, 200), (515, 1200)], fill=(80, 80, 80))

    # Traffic sign with garbled text
    draw.rectangle([(420, 250), (600, 450)], fill=(20, 100, 40),
                   outline=(0, 0, 0), width=3)
    add_garbled_text(draw, 435, 300, 150, 100)

    # Another sign
    draw.rectangle([(420, 500), (600, 700)], fill=(30, 60, 160),
                   outline=(0, 0, 0), width=3)
    add_garbled_text(draw, 435, 550, 150, 100)

    # Shop sign
    draw.rectangle([(100, 400), (310, 650)], fill=(190, 40, 30))
    add_garbled_text(draw, 120, 440, 170, 180)

    # Billboard
    draw.rectangle([(750, 300), (1050, 600)], fill=(30, 60, 80))
    draw.rectangle([(750, 300), (1050, 600)], outline=(0, 0, 0), width=4)
    add_garbled_text(draw, 780, 330, 240, 240)

    path = os.path.join(OUTPUT_DIR, "ep2_img3_street_signs.png")
    img.save(path, quality=95)
    print(f"  Saved: {path}")
    return path


def image4_real_comparison():
    """A real (non-AI) scene with clear readable text for comparison."""
    print("Generating image 4: Real comparison...")
    img, draw = create_base_scene((90, 85, 80))

    # Real looking store with CLEAR text
    draw.rectangle([(100, 200), (980, 1200)], fill=(100, 90, 80))

    # Store sign
    draw.rectangle([(250, 350), (830, 550)], fill=(20, 100, 30), outline=(0, 0, 0), width=3)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 60)
        draw.text((300, 380), "老王家面馆", fill=(255, 255, 255), font=font,
                 stroke_width=2, stroke_fill=(0, 0, 0))
        font_s = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 30)
        draw.text((320, 460), "正宗兰州拉面", fill=(255, 255, 200), font=font_s)
    except Exception:
        pass

    # Door
    draw.rectangle([(400, 650), (680, 1200)], fill=(60, 50, 40))
    # Clear window text
    try:
        font_w = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 28)
        draw.text((420, 700), "营业中", fill=(0, 200, 50), font=font_w)
        draw.text((420, 750), "早8:00 - 晚10:00", fill=(50, 50, 50), font=font_w)
    except Exception:
        pass

    path = os.path.join(OUTPUT_DIR, "ep2_img4_real_comparison.png")
    img.save(path, quality=95)
    print(f"  Saved: {path}")
    return path


if __name__ == "__main__":
    print("=" * 50)
    print("Generating Episode 2 Assets: AI Text Garbling")
    print("=" * 50)

    img1 = image1_store_sign()
    img2 = image2_tshirt_text()
    img3 = image3_street_signs()
    img4 = image4_real_comparison()

    print()
    print(f"All assets saved to: {OUTPUT_DIR}")
    print("Ready for pipeline.")

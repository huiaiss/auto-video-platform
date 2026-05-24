"""Generate Episode 2 images via Volcano Ark Seedream API — AI text garbling theme"""
import base64, os, sys, time
from openai import OpenAI

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT, "output", "ep2_assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Load .env if present
_env_path = os.path.join(ROOT, ".env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("SEEDREAM_API_KEY", "")
BASE_URL = os.environ.get("SEEDREAM_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

if not API_KEY:
    print("Error: SEEDREAM_API_KEY not set. Create .env file or set environment variable.")
    sys.exit(1)

MODELS = [
    "doubao-seedream-4-5-251128",
    "doubao-seedream-4-0-250828",
]

# Prompts designed to TRICK AI into generating text — which it will garble
PROMPTS = {
    "ep2_img1_store_sign": {
        "prompt": (
            "Street photography, a small Chinese convenience store at night, "
            "bright neon sign above the door with clearly visible Chinese characters "
            "showing the store name, glass window with promotional text stickers, "
            "warm yellow light spilling onto the wet pavement, rain puddles reflecting neon, "
            "cinematic cyberpunk mood, vertical 9:16 portrait, "
            "captured on Fujifilm X-T5 with 23mm f/1.4 lens, hyper-realistic details"
        ),
        "desc": "便利店招牌文字"
    },
    "ep2_img2_tshirt_text": {
        "prompt": (
            "Candid street fashion portrait, a young person wearing a white graphic t-shirt "
            "with bold printed slogan text across the chest, standing against a colorful graffiti wall, "
            "the t-shirt design includes Chinese characters and English words mixed together, "
            "natural sunlight, sharp focus on the t-shirt graphic details, "
            "editorial fashion photography, 85mm portrait lens, vertical 9:16, "
            "magazine quality, every letter on the shirt clearly visible"
        ),
        "desc": "T恤印刷文字"
    },
    "ep2_img3_street_signs": {
        "prompt": (
            "Busy Chinese city intersection, multiple street signs, billboards, and shop banners "
            "with Chinese text visible at various distances, traffic signs with characters, "
            "a large LED advertising screen showing promotional text, "
            "busy urban scene with pedestrians, golden hour lighting, "
            "wide-angle cityscape, vertical 9:16, ultra-detailed, "
            "every sign and character sharply rendered, photojournalism style"
        ),
        "desc": "街道招牌文字"
    },
    "ep2_img4_real_comparison": {
        "prompt": (
            "Real photograph aesthetic, a beautiful traditional Chinese tea house storefront, "
            "wooden carved sign with perfectly clear Chinese calligraphy characters reading the shop name, "
            "red lanterns hanging by the entrance, potted bamboo plants, "
            "natural afternoon sunlight, high-end architectural photography, "
            "clean sharp details, all text naturally readable, "
            "vertical 9:16, professional real estate photography quality"
        ),
        "desc": "真实文字对比图"
    },
}


def generate(prompt, model=None, size="1080x1920"):
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    models_to_try = [model] if model else MODELS

    for m in models_to_try:
        try:
            actual_size = "1440x2560" if "4-5" in m else size
            print(f"    Model: {m} ({actual_size})")
            resp = client.images.generate(
                model=m, prompt=prompt, size=actual_size,
                n=1, response_format="b64_json",
                extra_body={"watermark": False}
            )
            img_data = base64.b64decode(resp.data[0].b64_json)
            print(f"    OK: {len(img_data)//1024}KB")
            return img_data
        except Exception as e:
            print(f"    FAIL: {e}")
            continue
    return None


def main():
    print("=" * 55)
    print("  Episode 2 Image Generation — Seedream API")
    print(f"  Output: {ASSETS_DIR}")
    print("=" * 55)

    for key, info in PROMPTS.items():
        filename = f"{key}.png"
        out_path = os.path.join(ASSETS_DIR, filename)

        if os.path.exists(out_path) and os.path.getsize(out_path) > 50000:
            print(f"\n[{key}] {info['desc']} — EXISTS, skip")
            continue

        print(f"\n[{key}] {info['desc']}")
        img_data = generate(info["prompt"])
        if img_data:
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"  Saved: {filename}")
        else:
            print(f"  FAILED all models")

        time.sleep(1.5)

    print("\nDone.")


if __name__ == "__main__":
    main()

import json, re, os

def generate_terms(script, brand_name="", dispatcher=None):
    """Extract search terms from script for material matching (BGM, footage, SFX)."""
    if dispatcher is None:
        from generators.llm_providers import get_dispatcher
        dispatcher = get_dispatcher()
    
    beats = script.get("beats", [])
    texts = [b.get("text", "") for b in beats]
    all_text = " ".join(texts) or script.get("title", "")
    
    prompt = (
        "Extract 5-8 Chinese search keywords from this video script "
        "for finding stock video footage, images, and BGM.\n\n"
        "Script: " + all_text + "\n"
        "Brand: " + brand_name + "\n\n"
        "Return ONLY a JSON array of strings, no markdown."
    )
    
    try:
        resp = dispatcher.chat([
            {"role": "system", "content": "You extract search keywords from video scripts. Return only a JSON array."},
            {"role": "user", "content": prompt},
        ])
        if resp and resp.content:
            match = re.search(r'\[.*?\]', resp.content, re.DOTALL)
            if match:
                terms = json.loads(match.group())
                return [t for t in terms if len(t) > 1][:10]
    except Exception as e:
        print("Terms generation error:", e)
    return []


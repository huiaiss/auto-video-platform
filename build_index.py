#!/usr/bin/env python3
"""Build deploy/index.html for 隆江 LONGJIANG."""
import os, base64

B64 = """RE5EX0hUTUxfQ09OVEVOVA=="""  # placeholder

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy", "index.html")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(base64.b64decode(B64).decode("utf-8"))

print(f"Written {OUT}")

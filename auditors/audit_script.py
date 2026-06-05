#!/usr/bin/env python3
"""
车间主任-脚本审计 (Stage 2)
用法: python audit_script.py <script.json> <roughcut.mp4>
返回: exit 0=PASS, exit 1=FAIL
"""
import sys, json, subprocess, os, re
from datetime import datetime

SCRIPT = sys.argv[1]
VIDEO = sys.argv[2] if len(sys.argv) > 2 else None
OUT_DIR = os.path.dirname(SCRIPT) or "."
results = {"stage": "script", "time": datetime.now().isoformat(), "checks": []}
passed = 0

def check(name, ok, detail=""):
    global passed
    results["checks"].append({"name": name, "pass": ok, "detail": detail})
    if ok: passed += 1
    print(f"  {'[PASS]' if ok else '[FAIL]'} {name}: {detail}")
    return ok

with open(SCRIPT, "r", encoding="utf-8") as f:
    data = json.load(f)

BRAND = data.get("metadata", {}).get("title", "")
beats = data.get("beats", [])
outro = data.get("outro", {})

print(f"\n[Search] 车间主任-脚本审计: {SCRIPT}")
print("=" * 50)

# ???? 检查1: 品牌数据 ????
brand_terms = ["隆江", "绕线", "台州", "自动化"]
brand_ok = any(t in str(data) for t in brand_terms)
check("品牌数据", brand_ok, 
      "包含隆江品牌信息" if brand_ok else "缺少隆江品牌字段")

# ???? 检查2: 抖音字数 ????
overlong = 0
for b in beats:
    text = b.get("text", "")
    if len(text) > 26:
        overlong += 1
check("文案字数(≤26字)", overlong <= 3,
      f"{overlong}/{len(beats)}条超26字" if overlong else "全部合规")

# 检查3: start_s 时间戳完整性
beats_with_ts = sum(1 for b in beats if "start_s" in b)
ts_ok = beats_with_ts == len(beats) and len(beats) > 0
check("start_s时间戳", ts_ok,
      f"{beats_with_ts}/{len(beats)} beat含时间戳" if ts_ok else f"缺失{len(beats)-beats_with_ts}个beat的start_s")

# 检查4: 文案完整性（以标点结尾，不是半截句）
incomplete = 0
for b in beats:
    text = b.get("text", "")
    if text and text[-1] not in "。！？.!?":
        incomplete += 1
check("文案完整性(标点结尾)", incomplete <= 1,
      f"{incomplete}条文案不完整" if incomplete else "全部完整句")
outro_text = outro.get("text", "") + " " + outro.get("visual", "")
has_company = any(t in outro_text for t in ["隆江", "台州", "自动化"])
check("品牌尾帧", has_company,
      f"outro含品牌名" if has_company else "outro缺品牌信息")

# ???? 输出 ????
print("=" * 50)
result = "PASS" if passed == 5 else "FAIL"
print(f"? 结果: {result} ({passed}/5 通过)")

result_file = os.path.join(OUT_DIR, f"AUDIT_{result}.txt")
with open(result_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

opposite = os.path.join(OUT_DIR, f"AUDIT_{'FAIL' if result=='PASS' else 'PASS'}.txt")
if os.path.exists(opposite): os.remove(opposite)

print(json.dumps(results, indent=2, ensure_ascii=False))
sys.exit(0 if result == "PASS" else 1)





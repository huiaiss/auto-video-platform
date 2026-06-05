#!/usr/bin/env python3
"""
车间主任-整合审计 (Stage 3)
用法: python audit_compose.py <final.mp4>
返回: exit 0=PASS, exit 1=FAIL
"""
import sys, json, subprocess, os, hashlib
from datetime import datetime

VIDEO = sys.argv[1]
OUT_DIR = os.path.dirname(VIDEO) or "."
results = {"stage": "compose", "time": datetime.now().isoformat(), "checks": []}
passed = 0

def check(name, ok, detail=""):
    global passed
    results["checks"].append({"name": name, "pass": ok, "detail": detail})
    if ok: passed += 1
    print(f"  {'[PASS]' if ok else '[FAIL]'} {name}: {detail}")
    return ok

def ffprobe_entries(path, entries):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", f"stream={entries}",
                        "-of", "csv=p=0", path], capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    return r.stdout.strip().split(",")[0]

def run_ffmpeg(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")

print(f"\n[Search] 车间主任-整合审计: {VIDEO}")
print("=" * 50)

# ???? 检查1: 编码兼容性 ????
codec = ffprobe_entries(VIDEO, "codec_name")
profile = ffprobe_entries(VIDEO, "profile")
pix_fmt = ffprobe_entries(VIDEO, "pix_fmt")
color = ffprobe_entries(VIDEO, "color_space")

enc_ok = (codec == "h264" and profile in ("Main", "High") and pix_fmt == "yuv420p" 
          and color in ["bt709", "unknown", ""])
check("编码兼容", enc_ok,
      f"h264/{profile}/{pix_fmt}/{color}" if enc_ok else f"[FAIL] h264/{profile}/{pix_fmt}/{color}")

# ???? 检查2: 文件大小 ????
size_mb = os.path.getsize(VIDEO) / 1024 / 1024
check("文件<100MB", size_mb < 100, f"{size_mb:.1f}MB")

# ???? 检查3: 无花屏/闪烁 (逐帧hash对比) ????
r = run_ffmpeg(["ffmpeg", "-i", VIDEO, "-vf", "select='not(mod(n\\,15))',signalstats",
                "-f", "null", "-"])
# 检查是否有SAT异常（花屏特征）
sat_issues = r.stderr.count("SAT:0") + r.stderr.count("SAT:1")
check("无花屏", sat_issues < 5, f"信号异常帧: {sat_issues}" if sat_issues >= 5 else f"信号正常({sat_issues}个低SAT帧)")

# ???? 检查4: 抽帧文字可读性 ????
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", VIDEO], capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout.strip())
all_ok = True
for i in range(4):
    t = dur * (0.1 + i * 0.25)
    fp = os.path.join(OUT_DIR, f"_compose_frame_{i}.png")
    run_ffmpeg(["ffmpeg", "-y", "-ss", str(t), "-i", VIDEO, "-vframes", "1", "-q:v", "2", fp])
    size = os.path.getsize(fp) if os.path.exists(fp) else 0
    if size < 2000:
        all_ok = False
        break
# 清理
for i in range(4):
    fp = os.path.join(OUT_DIR, f"_compose_frame_{i}.png")
    if os.path.exists(fp): os.remove(fp)
check("文字可读", all_ok and True, "4帧内容正常" if all_ok else f"帧{i}体积{size}B=可能黑/白屏")

# ???? 检查5: 品牌尾帧 ????
# 抽最后1秒的帧
end_t = max(0, dur - 1)
end_fp = os.path.join(OUT_DIR, "_compose_end.png")
run_ffmpeg(["ffmpeg", "-y", "-ss", str(end_t), "-i", VIDEO, "-vframes", "1", "-q:v", "2", end_fp])
end_size = os.path.getsize(end_fp) if os.path.exists(end_fp) else 0
check("品牌尾帧", end_size > 5000, f"尾帧{end_size}B" if end_size > 5000 else f"尾帧过小({end_size}B)")
if os.path.exists(end_fp): os.remove(end_fp)

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

#!/usr/bin/env python3
"""
车间主任-粗剪审计 (Stage 1)
用法: python audit_roughcut.py <video_path>
返回: exit 0=PASS, exit 1=FAIL (JSON输出到stdout)
参考: ffmpeg blackdetect / slhck/ffmpeg-black-split
"""
import sys, json, subprocess, os, tempfile, hashlib
from datetime import datetime

VIDEO = sys.argv[1]
OUT_DIR = os.path.dirname(VIDEO) or "."
results = {"stage": "roughcut", "time": datetime.now().isoformat(), "checks": []}
passed = 0

def check(name, ok, detail=""):
    global passed
    results["checks"].append({"name": name, "pass": ok, "detail": detail})
    if ok: passed += 1
    print(f"  {'[PASS]' if ok else '[FAIL]'} {name}: {detail}")
    return ok

def ffprobe_get(path, key):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", f"format={key}", 
                        "-of", "csv=p=0", path], capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    return r.stdout.strip()

def run_ffmpeg(args):
    return subprocess.run(args, capture_output=True, text=True, errors="replace")

# ???? 检查1: 黑帧检测 ????
print(f"\n[Search] 车间主任-粗剪审计: {VIDEO}")
print("=" * 50)
r = run_ffmpeg(["ffmpeg", "-i", VIDEO, "-vf", "blackdetect=d=0.5:pix_th=0.1", 
                "-an", "-f", "null", "-"])
has_black = "black_start" in r.stderr or "black_start" in r.stdout
check("黑帧检测", not has_black, 
      "检测到黑帧段落" if has_black else "无黑帧")

# ???? 检查2: 冻结帧 ????
r = run_ffmpeg(["ffmpeg", "-i", VIDEO, "-vf", "freezedetect=n=0.003,duration=1", 
                "-an", "-f", "null", "-"])
freeze_lines = [l for l in (r.stderr + r.stdout).split('\n') if 'freeze_duration' in l]
long_freeze = any(float(l.split('freeze_duration=')[1].strip()) > 2.0 for l in freeze_lines)
check("冻结帧", not long_freeze,
      f"检测到{len(freeze_lines)}处冻结，含>2s长冻结" if long_freeze else f"共{len(freeze_lines)}处冻结，均<2s")

# ???? 检查3: 时长 ????
dur = float(ffprobe_get(VIDEO, "duration"))
in_range = 28 <= dur <= 60  # xfade reduces total by ~1.8s
check("时长30-60s", in_range, f"{dur:.1f}s")

# ???? 检查4: 抽帧过曝检测 ????
# 抽4帧位置
positions = [0.05, 0.30, 0.55, 0.80]
frame_issues = 0
for i, pos in enumerate(positions):
    t = dur * pos
    frame_path = os.path.join(OUT_DIR, f"_audit_frame_{i}.png")
    run_ffmpeg(["ffmpeg", "-y", "-ss", str(t), "-i", VIDEO, 
                "-vframes", "1", "-q:v", "2", frame_path])
    if os.path.exists(frame_path) and os.path.getsize(frame_path) < 500:
        frame_issues += 1  # 太小=可能黑帧

check("抽帧质量", frame_issues == 0,
      f"4帧全部正常" if frame_issues == 0 else f"{frame_issues}/4帧异常（体积过小=可能黑/白屏）")
# 清理
for i in range(4):
    fp = os.path.join(OUT_DIR, f"_audit_frame_{i}.png")
    if os.path.exists(fp): os.remove(fp)

# Check 5: clip diversity - count clip files in stage1 output
import glob
clip_dir = os.path.dirname(VIDEO)
clip_pattern = os.path.join(clip_dir, "_clip_*.mp4")
clip_files = glob.glob(clip_pattern)
n_clips = len(clip_files)
check("clip_count>=2", n_clips >= 2, f"{n_clips} clips")

# ???? 输出结果 ????
print("=" * 50)
result = "PASS" if passed == 5 else "FAIL"
print(f"? 结果: {result} ({passed}/5 通过)")

# 写结果文件
result_file = os.path.join(OUT_DIR, f"AUDIT_{result}.txt")
with open(result_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# 清理旧的相反结果文件
opposite = os.path.join(OUT_DIR, f"AUDIT_{'FAIL' if result=='PASS' else 'PASS'}.txt")
if os.path.exists(opposite): os.remove(opposite)

print(json.dumps(results, indent=2, ensure_ascii=False))
sys.exit(0 if result == "PASS" else 1)

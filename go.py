#!/usr/bin/env python
"""Auto Video Platform — 一键管线：素材诊断→粗剪→脚本→合成→审计"""
import os, sys, subprocess, shutil, glob

ROOT = r"D:\auto-video-platform"
FOOTAGE = "D:/隆江视频素材/IMG_034*.MP4"

def run(cmd, desc, timeout=600):
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    r = subprocess.run(cmd, capture_output=False, timeout=timeout)
    return r.returncode == 0

def main():
    os.chdir(ROOT)
    python = sys.executable

    # 清 Stage 3 缓存
    s3 = os.path.join(ROOT, "output", "stage3")
    if os.path.exists(s3):
        shutil.rmtree(s3)
    os.makedirs(s3)

    # Step 0: 素材诊断
    if not run([python, "pipeline.py", "0", FOOTAGE], "Stage 0 — 素材诊断"):
        print("  FAILED at Stage 0"); return False

    # Step 1: 粗剪
    if not run([python, "pipeline.py", "1", FOOTAGE], "Stage 1 — 视频粗剪"):
        print("  FAILED at Stage 1"); return False

    # 审计 1
    roughcut = os.path.join(ROOT, "output", "stage1", "roughcut.mp4")
    if not run([python, "auditors/audit_roughcut.py", roughcut], "审计 1 — 粗剪审计"):
        print("  FAILED at Stage 1 audit"); return False

    # Step 2: 脚本
    if not run([python, "pipeline.py", "2"], "Stage 2 — 脚本生成"):
        print("  FAILED at Stage 2"); return False

    # 审计 2
    script = os.path.join(ROOT, "output", "stage2", "script.json")
    if not run([python, "auditors/audit_script.py", script, roughcut], "审计 2 — 脚本审计"):
        print("  FAILED at Stage 2 audit"); return False

    # Step 3: 合成
    if not run([python, "pipeline.py", "3"], "Stage 3 — 视频合成"):
        print("  FAILED at Stage 3"); return False

    # 审计 3
    final = os.path.join(ROOT, "output", "stage3", "final.mp4")
    if not run([python, "auditors/audit_compose.py", final, script], "审计 3 — 合成审计"):
        print("  FAILED at Stage 3 audit"); return False

    sz = os.path.getsize(final)//1024
    print(f"\n{'='*60}")
    print("  [OK] 全部通过！")
    print(f"  final.mp4: {sz}KB")

    # 显示发布计划摘要
    pp = os.path.join(ROOT, "output", "stage3", "publish_plan.json")
    if os.path.exists(pp):
        import json
        with open(pp, encoding="utf-8") as f:
            plan = json.load(f)
        print(f"\n  发布计划 (publish_plan.json):")
        for pname, pinfo in plan.get("platforms", {}).items():
            print(f"    {pname:12s} {pinfo['title'][:25]:25s}  {pinfo['best_time'][0]}发布")
    print(f"{'='*60}")
    return True

if __name__ == "__main__":
    ok = main()
    subprocess.run([sys.executable, "save_context.py"], capture_output=True)
sys.exit(0 if ok else 1)


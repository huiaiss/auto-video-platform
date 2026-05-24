"""End-to-end test for JianyingDraftExporter."""
import os, sys, json, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from builders.jianying_exporter import JianyingDraftExporter, find_jianying_draft_dir

# --- Mock component storyboard (same format as StoryboardMapper output) ---
TEST_IMG = os.path.join(os.path.dirname(__file__), "..", "抖音参考视频",
                        "ai-zhaoyaojing-ep1", "assets", "img2_group_photo.png")
TEST_IMG = os.path.normpath(TEST_IMG)
REAL_IMG = os.path.join(os.path.dirname(__file__), "..", "抖音参考视频",
                        "ai-zhaoyaojing-ep1", "assets", "real_group_generated.png")
REAL_IMG = os.path.normpath(REAL_IMG)

mock_storyboard = {
    "scenes": [
        {
            "component": "social-frame",
            "start": 0.0,
            "duration": 4.0,
            "config": {
                "img_src": TEST_IMG,
                "username": "小美",
                "avatar_letter": "美",
                "post_text": "聚会太开心啦！大家猜猜这是哪里？",
                "post_time": "2小时前",
                "likes": "156",
                "comments": [
                    ("小芳", "在哪里拍的？好好看！"),
                    ("阿杰", "这是AI生成的吧？有点假"),
                    ("小美 回复 阿杰", "怎么可能~"),
                ],
            },
        },
        {
            "component": "glitch-transition",
            "start": 3.5,
            "duration": 2.0,
            "config": {},
        },
        {
            "component": "reveal-text",
            "start": 5.0,
            "duration": 3.0,
            "config": {
                "img_src": TEST_IMG,
                "reveal_text": "它不是真人拍的。\n是AI生成的。",
                "anticipation_text": "来，我放大三个细节给你看 ↓",
            },
        },
        {
            "component": "zoom-analyze",
            "start": 7.5,
            "duration": 8.0,
            "config": {
                "img_src": TEST_IMG,
                "label": "看手指破绽",
                "keyword_text": "六指异常",
                "keyword_color": "#ff1744",
                "markers": [
                    {"x": 200, "y": 800, "w": 140, "h": 140, "delay": 1.5},
                    {"x": 400, "y": 900, "w": 100, "h": 100, "delay": 2.3},
                ],
                "data_badge": {"big": "87%", "sub": "异常指数"},
                "count_badge": {"value": "1"},
            },
        },
        {
            "component": "compare-split",
            "start": 15.5,
            "duration": 10.0,
            "config": {
                "ai_img": TEST_IMG,
                "real_img": REAL_IMG,
                "checks": [
                    {"label": "手指数量", "fail": "异常", "pass": "正常"},
                    {"label": "五官对称", "fail": "歪斜", "pass": "对称"},
                    {"label": "关节弯曲", "fail": "僵直", "pass": "自然"},
                ],
                "summary_text": "记住查三处：手 · 脸 · 关节",
            },
        },
        {
            "component": "outro",
            "start": 25.5,
            "duration": 10.0,
            "config": {
                "title": "AI照妖镜",
                "subtitle": "关注我，下次被骗的不是你",
                "teaser": "下期见 →",
                "logo_char": "鉴",
            },
        },
    ],
    "audio_src": "",
    "bgm_src": "",
    "global_overlays": {
        "scan_show_at": 7.5,
        "scan_hide_at": 23.5,
    },
    "metadata": {
        "title": "AI照妖镜 - 测试导出",
        "author": "auto-video-platform",
        "video_type": "ai-flaw-detect",
    },
}


def test_find_draft_dir():
    """Test Jianying draft directory discovery."""
    d = find_jianying_draft_dir()
    print(f"[1] Draft dir: {d}")
    if d:
        print("    PASS: Draft directory found")
    else:
        print("    WARN: No Jianying draft directory found (Jianying may not be installed)")
    return d


def test_export(draft_dir=None):
    """Test full export flow."""
    print(f"[2] Creating exporter...")
    try:
        exporter = JianyingDraftExporter(draft_dir=draft_dir)
        print("    PASS: Exporter created")
    except ImportError as e:
        print(f"    FAIL: {e}")
        return None

    print(f"[3] Running export...")
    try:
        draft_path = exporter.export(
            mock_storyboard,
            draft_name=f"AI_Test_{uuid.uuid4().hex[:6]}",
        )
        print(f"    PASS: Draft exported to: {draft_path}")
        return draft_path
    except Exception as e:
        print(f"    FAIL: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_draft_contents(draft_path):
    """Verify draft folder/file structure."""
    if not draft_path or not os.path.exists(draft_path):
        print("[4] SKIP: No draft to inspect")
        return

    print(f"[4] Inspecting draft: {draft_path}")

    # Handle both directory and file paths
    if os.path.isdir(draft_path):
        contents = os.listdir(draft_path)
        print(f"    Contents: {contents}")
        has_json = any(f.endswith(".json") for f in contents)
        has_materials = "materials" in contents
        print(f"    Has JSON: {'PASS' if has_json else 'FAIL'}")
        print(f"    Has materials: {'PASS' if has_materials else 'FAIL'}")
        if has_json:
            json_file = next(f for f in contents if f.endswith(".json"))
            json_path = os.path.join(draft_path, json_file)
        else:
            json_path = None
    else:
        # It's a file (standalone mode)
        json_path = draft_path
        draft_dir = os.path.dirname(draft_path)
        print(f"    Draft dir: {draft_dir}")
        if os.path.exists(draft_dir):
            contents = os.listdir(draft_dir)
            print(f"    Contents: {contents}")
            has_materials = "materials" in contents
            print(f"    Has materials: {'PASS' if has_materials else 'FAIL'}")

    if json_path and os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        if "tracks" in data:
            tracks = data["tracks"]
            print(f"    Track count: {len(tracks)}")
            for t in tracks[:8]:  # first 8 tracks
                segs = t.get("segments", [])
                print(f"      Track type={t.get('type', '?')}, segments={len(segs)}")
        elif "materials" in data:
            print(f"    Materials count: {len(data['materials'])}")
            print(f"    Text segments: {len(data.get('content', {}).get('texts', []))}")
        else:
            print(f"    Top keys: {list(data.keys())[:10]}")
        print(f"    File size: {os.path.getsize(json_path):,} bytes")


if __name__ == "__main__":
    print("=" * 50)
    print("JianyingDraftExporter — End-to-End Test")
    print("=" * 50)
    print()

    draft_dir = test_find_draft_dir()
    print()

    # Export even without Jianying installed (creates standalone draft)
    draft_path = test_export(draft_dir)
    print()

    test_draft_contents(draft_path)
    print()
    print("=" * 50)
    print("Test complete")

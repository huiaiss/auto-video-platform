# -*- coding: utf-8 -*-
"""豆包语音合成2.0 本地代理 — OpenAI 兼容 → Volcengine Speech API.

Usage:
    python generators/ark_tts_proxy.py          # 启动代理 (默认 :8791)

环境变量:
    VOLC_TTS_API_KEY  新版 API Key（从 https://console.volcengine.com/speech/api-key 获取）
    VOLC_TTS_RESOURCE_ID  资源 ID（默认 seed-tts-2.0）
"""

import json, os, sys, uuid, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PROXY_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
SPEECH_API_V1 = "https://openspeech.bytedance.com/api/v1/tts"
SPEECH_API_V3 = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"

# 从 .env 或环境变量读取
API_KEY = os.environ.get("VOLC_TTS_API_KEY", "")
RESOURCE_ID = os.environ.get("VOLC_TTS_RESOURCE_ID", "seed-tts-2.0")

# 2.0 音色映射（新版）
VOICE_MAP_V3 = {
    "zh_female_2": "zh_female_vv_uranus_bigtts",
    "zh_female_1": "zh_female_vv_uranus_bigtts",
    "zh_male_1": "zh_male_m191_uranus_bigtts",
    "zh_male_2": "zh_male_m191_uranus_bigtts",
    "zh_female_cancan": "zh_female_cancan_mars_bigtts",
}

class ArkTTSHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        path = self.path.rstrip("/")
        if not path.endswith("/v1/audio/speech"):
            self._json(404, {"error": "not found"})
            return

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b"{}"
        try:
            req = json.loads(body.decode("utf-8")) if body else {}
        except UnicodeDecodeError:
            try:
                req = json.loads(body.decode("gbk")) if body else {}
            except Exception:
                req = {}
        except Exception:
            req = {}

        text = req.get("input", "")
        if not text:
            self._json(400, {"error": "input is required"})
            return

        model = req.get("model", "volcano_tts")
        voice = req.get("voice", "zh_female_1")
        speed = req.get("speed", 1.0)
        fmt = req.get("response_format", "mp3")

        encoding = "mp3" if fmt == "mp3" else "wav"
        voice_type = VOICE_MAP_V3.get(voice, voice)

        if not API_KEY:
            self._json(401, {
                "error": "missing_credentials",
                "message": "请配置 VOLC_TTS_API_KEY",
                "guide": "打开 https://console.volcengine.com/speech/api-key 创建 API Key"
            })
            return

        # v3 API — 新版豆包语音合成2.0
        payload_v3 = json.dumps({
            "user": {"uid": "codex_tts"},
            "req_params": {
                "text": text,
                "speaker": voice_type,
                "audio_params": {
                    "format": encoding,
                },
            },
        }).encode("utf-8")

        try:
            http_req = urllib.request.Request(
                SPEECH_API_V3, data=payload_v3,
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": API_KEY,
                    "X-Api-Resource-Id": RESOURCE_ID,
                }
            )
            with urllib.request.urlopen(http_req, timeout=120) as resp:
                # Response is chunked JSON with base64 audio
                raw = b""
                while True:
                    chunk = resp.read(4096)
                    if not chunk:
                        break
                    raw += chunk

            # Parse chunked JSON and aggregate base64 audio
            import base64
            audio_data = b""
            text_data = raw.decode("utf-8")
            for line in text_data.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get("code") == 0 and obj.get("data"):
                        audio_data += base64.b64decode(obj["data"])
                except Exception:
                    pass

            if not audio_data:
                self._json(500, {"error": "empty_audio", "detail": text_data[:500]})
                return

        except urllib.error.HTTPError as e:
            err = e.read().decode()[:300] if e.fp else ""
            self._json(e.code, {"error": "speech_api_error", "detail": err})
            return

        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(audio_data)))
        self._cors()
        self.end_headers()
        self.wfile.write(audio_data)

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def log_message(self, format, *args):
        print(f"[ArkTTS] {args[0]} {args[1]} {args[2]}", flush=True)


if __name__ == "__main__":
    if not API_KEY:
        print("[ArkTTS] ! 请设置 VOLC_TTS_API_KEY")
        print("[ArkTTS] 获取: https://console.volcengine.com/speech/api-key")
        print()

    server = HTTPServer(("0.0.0.0", PROXY_PORT), ArkTTSHandler)
    print(f"[ArkTTS Proxy] Running on :{PROXY_PORT}")
    print(f"  POST http://localhost:{PROXY_PORT}/v1/audio/speech")
    print(f"  Resource: {RESOURCE_ID}")
    print(f"  API Key:  {API_KEY[:12] if API_KEY else '(not set)'}...")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

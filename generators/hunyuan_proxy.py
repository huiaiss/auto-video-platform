"""腾讯混元本地代理 — OpenAI兼容请求 → TC3-HMAC-SHA256 签名 → 腾讯云API.

Usage:
    python generators/hunyuan_proxy.py          # 启动代理 (默认 :8789)
    # llm_config.json 配:
    # "base_url": "http://localhost:8789/v1"
"""

import json, os, sys, hashlib, hmac, time, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

HUNYUAN_ENDPOINT = "hunyuan.tencentcloudapi.com"
HUNYUAN_SERVICE = "hunyuan"
HUNYUAN_VERSION = "2023-09-01"
HUNYUAN_ACTION = "ChatCompletions"
HUNYUAN_REGION = "ap-guangzhou"

SECRET_ID = os.environ.get("HUNYUAN_SECRET_ID", "")
SECRET_KEY = os.environ.get("HUNYUAN_SECRET_KEY", "")

MODEL_MAP = {
    "hunyuan-turbo": "hunyuan-turbo",
    "hunyuan-pro": "hunyuan-pro",
    "hunyuan-standard": "hunyuan-standard",
    "hunyuan-lite": "hunyuan-lite",
}

def sign_tc3(payload_str):
    service = HUNYUAN_SERVICE
    host = HUNYUAN_ENDPOINT
    algorithm = "TC3-HMAC-SHA256"
    timestamp = int(time.time())
    date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))

    http_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json"
    payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
    canonical_headers = f"content-type:{ct}\nhost:{host}\nx-tc-action:{HUNYUAN_ACTION.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    canonical_request = f"{http_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"

    credential_scope = f"{date}/{service}/tc3_request"
    string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    def _hmac_sha256(key, msg):
        return hmac.new(key if isinstance(key, bytes) else key.encode("utf-8"),
                        msg.encode("utf-8"), hashlib.sha256).digest()

    secret_date = _hmac_sha256(f"TC3{SECRET_KEY}", date)
    secret_service = _hmac_sha256(secret_date, service)
    secret_signing = _hmac_sha256(secret_service, "tc3_request")
    signature = _hmac_sha256(secret_signing, string_to_sign).hex()

    authorization = f"{algorithm} Credential={SECRET_ID}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    headers = {
        "Content-Type": ct,
        "Host": host,
        "X-TC-Action": HUNYUAN_ACTION,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": HUNYUAN_VERSION,
        "X-TC-Region": HUNYUAN_REGION,
        "Authorization": authorization,
    }
    return headers, f"https://{host}"


class HunyuanProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/v1/chat/completions", "/v1/models"):
            self._json(404, {"error": "not found"})
            return

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b"{}"
        req = json.loads(body) if body else {}

        if path == "/v1/models":
            self._json(200, {"object": "list", "data": [{"id": m, "object": "model"} for m in MODEL_MAP]})
            return

        model = req.get("model", "hunyuan-lite")
        tc_model = MODEL_MAP.get(model, model)
        messages = req.get("messages", [])
        tc_messages = [{"Role": m.get("role"), "Content": m.get("content", "")} for m in messages]
        temperature = req.get("temperature", 0.7)
        max_tokens = req.get("max_tokens", 2048)

        payload = {
            "Model": tc_model,
            "Messages": tc_messages,
            "Temperature": temperature,
            "TopP": 1.0,
        }

        payload_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        headers, url = sign_tc3(payload_str)

        import urllib.request
        try:
            http_req = urllib.request.Request(url, data=payload_str.encode("utf-8"), headers=headers)
            with urllib.request.urlopen(http_req, timeout=60) as resp:
                raw = json.loads(resp.read())
                # Tencent Cloud wraps everything in {"Response": {...}}
                result = raw.get("Response", raw)

            import sys as _sys
            print(f"[HunyuanProxy] Sent model={tc_model} msg_count={len(tc_messages)}", flush=True)
            print(f"[HunyuanProxy] Got Choices: {len(result.get('Choices', []))}", flush=True)
            if not result.get('Choices'):
                print(f"[HunyuanProxy] Response keys: {list(result.keys())}", flush=True)
                print(f"[HunyuanProxy] Raw snippet: {json.dumps(result, ensure_ascii=False)[:500]}", flush=True)

            choices = []
            for c in result.get("Choices", []):
                choices.append({
                    "index": c.get("Index", 0),
                    "message": {"role": "assistant", "content": c.get("Message", {}).get("Content", "")},
                    "finish_reason": c.get("FinishReason", "stop"),
                })

            usage = result.get("Usage", {})
            openai_resp = {
                "id": result.get("Id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
                "object": "chat.completion",
                "created": result.get("Created", int(time.time())),
                "model": model,
                "choices": choices,
                "usage": {
                    "prompt_tokens": usage.get("PromptTokens", 0),
                    "completion_tokens": usage.get("CompletionTokens", 0),
                    "total_tokens": usage.get("TotalTokens", 0),
                },
            }
            self._json(200, openai_resp)

        except urllib.error.HTTPError as e:
            err_body = e.read().decode()[:500]
            self._json(e.code, {"error": {"message": err_body, "code": e.code}})
        except Exception as e:
            self._json(500, {"error": {"message": str(e), "code": 500}})

    def _json(self, code, data):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8789
    if not SECRET_ID or not SECRET_KEY:
        print("ERROR: Set HUNYUAN_SECRET_ID and HUNYUAN_SECRET_KEY")
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", port), HunyuanProxyHandler)
    print(f"[HunyuanProxy] Running on :{port}")
    print(f"  → http://localhost:{port}/v1/chat/completions")
    print(f"  → http://localhost:{port}/v1/models")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[HunyuanProxy] Stopped")

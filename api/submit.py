import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BASE = "https://salta7.store"

# Overwrite the token configuration with your live dashboard value
HEADERS = {
    "Authorization": "Bearer YOUR_NEWLY_COPIED_TOKEN_HERE",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except Exception:
            content_length = 0
            
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as json_err:
            self._send_response({"error": "Failed to decode payload JSON", "details": str(json_err)}, 400)
            return

        raw_text = ""
        if isinstance(data, dict):
            raw_text = data.get('user_input') or data.get('tokens') or data.get('text') or data.get('data') or ""
        
        if isinstance(data, list):
            tokens_list = [str(item).strip() for item in data if str(item).strip()]
        else:
            tokens_list = [line.strip() for line in str(raw_text).split('\n') if line.strip()]
        
        if not tokens_list and isinstance(data, dict) and data:
            first_val = list(data.values())
            tokens_list = [line.strip() for line in str(first_val).split('\n') if line.strip()]

        if not tokens_list:
            self._send_response({"error": "No token entries parsed from frontend layout data payload."}, 400)
            return
            
        target_url = f"{BASE}/task/create"
        payload_bytes = json.dumps({"tool": "check", "tokens": tokens_list}).encode('utf-8')
        
        req = urllib.request.Request(target_url, data=payload_bytes, headers=HEADERS, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_body = response.read().decode('utf-8')
                try:
                    response_payload = json.loads(res_body)
                except Exception:
                    response_payload = {"status": "success", "raw_response": res_body[:200]}
                
                self._send_response(response_payload, 200)
                
        except urllib.error.HTTPError as http_err:
            try:
                err_details = http_err.read().decode('utf-8')
                try:
                    err_json = json.loads(err_details)
                except Exception:
                    err_json = err_details[:200]
            except Exception:
                err_json = "Could not extract error body detail metadata"
                
            self._send_response({
                "error": "Upstream service error status",
                "status_code": http_err.code,
                "details": err_json
            }, http_err.code if http_err.code else 502)
            
        except urllib.error.URLError as net_err:
            self._send_response({
                "error": "Failed to connect to upstream service host via urllib",
                "details": str(net_err.reason)
            }, 503)
        except Exception as e:
            self._send_response({
                "error": "Internal processor script runtime exception",
                "details": str(e)
            }, 500)

    def _send_response(self, payload, status_code):
        try:
            self.send_header('Content-type', 'application/json')
            self.send_response(status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        except Exception:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

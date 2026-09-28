import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

BASE = "https://salta7.store"

HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
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
            if not raw_text and data:
                for val in data.values():
                    if isinstance(val, str) and len(val) > len(raw_text):
                        raw_text = val
        
        if isinstance(data, list):
            lines = [str(item).strip() for item in data if str(item).strip()]
        else:
            lines = [line.strip() for line in str(raw_text).split('\n') if line.strip()]

        tokens_list = [item for item in lines if item]

        if not tokens_list:
            self._send_response({"error": "No lines parsed from payload"}, 400)
            return
            
        # Send task creation request directly to Salta7 Store
        create_url = f"{BASE}/task/create"
        create_payload = json.dumps({"tool": "check", "tokens": tokens_list}).encode('utf-8')
        
        req = urllib.request.Request(create_url, data=create_payload, headers=HEADERS, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                create_res = json.loads(response.read().decode('utf-8'))
                
            # Deliver the job payload directly back to your front-end layout instantly
            self._send_response(create_res, 200)
                
        except urllib.error.HTTPError as http_err:
            try:
                err_json = json.loads(http_err.read().decode('utf-8'))
            except Exception:
                err_json = "Handshake authorization or balance failure"
            self._send_response({"error": "Upstream error mapping", "status": http_err.code, "details": err_json}, http_err.code)
        except Exception as e:
            self._send_response({"error": "Internal processor workflow failure exception", "details": str(e)}, 500)

    def _send_response(self, payload, status_code):
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        except Exception:
            pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
        except Exception:
            pass

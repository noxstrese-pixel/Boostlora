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

        # 1. Grab base parameters required always
        mode = data.get('mode', 'stock') # 'stock' or 'byot'
        invite_code = data.get('invite', '')

        if not invite_code:
            self._send_response({"error": "A server invite code or link is strictly required."}, 400)
            return

        # 2. Build the exact API outbound body based on chosen mode
        api_payload = {
            "tool": "boost",
            "mode": mode,
            "invite": invite_code
        }

        if mode == 'stock':
            # Stock mode uses shop inventory counts
            api_payload["boosts"] = int(data.get('boosts', 2))
            if data.get('product'):
                api_payload["product"] = data.get('product')
        else:
            # BYOT mode accepts user pasted tokens directly
            raw_text = data.get('user_tokens_input', '')
            lines = [line.strip() for line in str(raw_text).split('\n') if line.strip()]
            
            if not lines:
                self._send_response({"error": "No tokens were pasted in the input area."}, 400)
                return
                
            api_payload["tokens"] = lines
            api_payload["boosts_needed"] = int(data.get('boosts_needed', 0))

        # Optional Profile Humanizer addition
        if data.get('humanize'):
            api_payload["humanize"] = data.get('humanize')

        # 3. Fire request to Salta7 task execution system
        target_url = f"{BASE}/task/create"
        payload_bytes = json.dumps(api_payload).encode('utf-8')
        req = urllib.request.Request(target_url, data=payload_bytes, headers=HEADERS, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_body = response.read().decode('utf-8')
                self._send_response(json.loads(res_body), 200)
                
        except urllib.error.HTTPError as http_err:
            try:
                err_json = json.loads(http_err.read().decode('utf-8'))
            except Exception:
                err_json = "Insufficent wallet store balance or invalid request inputs"
            self._send_response({"error": "Upstream booster system error", "status": http_err.code, "details": err_json}, http_err.code)
        except Exception as e:
            self._send_response({"error": "Internal booster gateway handler error", "details": str(e)}, 500)

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

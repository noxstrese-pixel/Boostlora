import json
import requests
from http.server import BaseHTTPRequestHandler

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNDBYQN5"}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read incoming data payload
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception:
            self._send_response({"error": "Invalid JSON format received"}, 400)
            return

        raw_text = data.get('user_input', '')
        tokens_list = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        if not tokens_list:
            self._send_response({"error": "No token entries parsed."}, 400)
            return
            
        # 2. Forward payload to upstream api server
        try:
            r = requests.post(
                f"{BASE}/task/create", 
                headers=HEADERS, 
                json={"tool": "check", "tokens": tokens_list},
                timeout=15
            )
            
            if not r.ok:
                self._send_response({
                    "error": "Upstream service error status",
                    "status_code": r.status_code,
                    "details": r.text[:200]
                }, 502)
                return
                
            self._send_response(r.json(), 200)
            
        except requests.exceptions.RequestException as network_err:
            self._send_response({
                "error": "Failed to reach upstream server database",
                "details": str(network_err)
            }, 503)
        except Exception as e:
            self._send_response({
                "error": "Internal processing crash",
                "details": str(e)
            }, 500)

    def _send_response(self, payload, status_code):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        # Handle CORS safety checks if tablet is calling from another domain
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_OPTIONS(self):
        # Handles automated pre-flight security requests sent by tablets/browsers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

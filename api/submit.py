import json
import requests
from http.server import BaseHTTPRequestHandler

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNDBYQN5"}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Safely parse Content-Length to read payload bytes
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except Exception:
            content_length = 0
            
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        # 2. Prevent JSON structural crashes 
        try:
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception as json_err:
            self._send_response({"error": "Failed to decode JSON payload", "details": str(json_err)}, 400)
            return

        # 3. Check every possible key name your frontend could be sending
        raw_text = ""
        if isinstance(data, dict):
            raw_text = data.get('user_input') or data.get('tokens') or data.get('text') or data.get('data') or ""
        
        # 4. Extract token items and split lines cleanly
        if isinstance(data, list):
            tokens_list = [str(item).strip() for item in data if str(item).strip()]
        else:
            tokens_list = [line.strip() for line in str(raw_text).split('\n') if line.strip()]
        
        # If fallback key checks failed, grab the first available value in the dictionary object
        if not tokens_list and isinstance(data, dict) and data:
            first_val = list(data.values())[0]
            if isinstance(first_val, list):
                tokens_list = [str(i).strip() for i in first_val if str(i).strip()]
            else:
                tokens_list = [line.strip() for line in str(first_val).split('\n') if line.strip()]

        if not tokens_list:
            self._send_response({"error": "No token entries parsed from frontend layout payload."}, 400)
            return
            
        # 5. Execute outbound API request to salta7
        try:
            r = requests.post(
                f"{BASE}/task/create", 
                headers=HEADERS, 
                json={"tool": "check", "tokens": tokens_list},
                timeout=20
            )
            
            # Pass upstream status blocks cleanly without crashing
            if not r.ok:
                try:
                    upstream_details = r.json()
                except Exception:
                    upstream_details = r.text[:150]
                    
                self._send_response({
                    "error": "Upstream service error status",
                    "status_code": r.status_code,
                    "details": upstream_details
                }, r.status_code if r.status_code else 502)
                return
                
            try:
                response_payload = r.json()
            except Exception:
                response_payload = {"status": "success", "raw_response": r.text[:200]}
                
            self._send_response(response_payload, 200)
            
        except requests.exceptions.RequestException as network_err:
            self._send_response({
                "error": "Failed to connect to upstream service host",
                "details": str(network_err)
            }, 503)
        except Exception as e:
            self._send_response({
                "error": "Internal execution crash exception",
                "details": str(e)
            }, 500)

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
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

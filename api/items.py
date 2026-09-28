import json
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = "https://salta7.store"

# Handshake headers include the desktop spoofing string to pass the database firewall
HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Safely parse incoming query parameters from the frontend request URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Grab job_id and after params sent by your iPad front-end app
        job_id = query_params.get('job_id', [''])[0]
        after = query_params.get('after', ['0'])[0]
        
        if not job_id:
            self._send_response({"error": "Missing required job_id query parameter."}, 400)
            return

        # 2. Construct clean outbound polling URL to Salta7 database
        target_url = f"{BASE}/task/items?job_id={job_id}&after={after}"
        req = urllib.request.Request(target_url, headers=HEADERS, method='GET')
        
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                res_body = response.read().decode('utf-8')
                try:
                    response_payload = json.loads(res_body)
                except Exception:
                    response_payload = {"status": "success", "raw_response": res_body[:200]}
                
                # Pass the fresh account data directly back to the front-end interface loop
                self._send_response(response_payload, 200)
                
        except urllib.error.HTTPError as http_err:
            try:
                err_json = json.loads(http_err.read().decode('utf-8'))
            except Exception:
                err_json = "Database connection rejected query parameters"
            self._send_response({"error": "Upstream polling failure", "status": http_err.code, "details": err_json}, http_err.code)
        except Exception as e:
            self._send_response({"error": "Internal items script crash exception", "details": str(e)}, 500)

    def _send_response(self, payload, status_code):
        try:
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        except Exception:
            pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()
        except Exception:
            pass

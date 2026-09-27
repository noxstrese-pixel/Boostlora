import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNDBYQN5"}

# Catch-all routing decorators prevent Vercel directory mapping issues 
# by capturing requests sent directly to "/" or any deeper subpaths.
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def handler(path):
    data = request.get_json() or {}
    raw_text = data.get('user_input', '')
    
    tokens_list = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    if not tokens_list:
        return jsonify({"error": "No token entries parsed."}), 400
        
    try:
        # Submit the payload to your upstream database/api endpoint
        r = requests.post(
            f"{BASE}/task/create", 
            headers=HEADERS, 
            json={"tool": "check", "tokens": tokens_list}
        )
        
        # Guard clause: If salta7.store is down or returns HTML instead of JSON,
        # handle it gracefully here instead of throwing a parsing exception.
        if not r.ok:
            return jsonify({
                "error": "Upstream service error status",
                "status_code": r.status_code,
                "details": r.text[:200]
            }), 502
            
        return jsonify(r.json())
        
    except requests.exceptions.RequestException as network_err:
        return jsonify({
            "error": "Failed to establish a network handshake with upstream server",
            "details": str(network_err)
        }), 503
    except Exception as e:
        return jsonify({
            "error": "Internal processing crash inside backend function execution",
            "details": str(e)
        }), 500

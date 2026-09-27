import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNDBYQN5"}

# The catch-all wrapper captures both structural route path versions
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
    # Ensure data payload safely falls back to dictionary structures
    try:
        data = request.get_json() or {}
    except Exception:
        return jsonify({"error": "Invalid JSON format received in request body"}), 400

    raw_text = data.get('user_input', '')
    tokens_list = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    if not tokens_list:
        return jsonify({"error": "No token entries parsed."}), 400
        
    try:
        r = requests.post(
            f"{BASE}/task/create", 
            headers=HEADERS, 
            json={"tool": "check", "tokens": tokens_list},
            timeout=10 # Prevents the function from timing out indefinitely
        )
        
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

# Expose 'app' object explicitly for Vercel's serverless WSGI runtime environment
# Do not call app.run() here as it causes Vercel deployments to crash

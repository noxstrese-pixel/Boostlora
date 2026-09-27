
import json
import requests
from flask import Flask, request, jsonify

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5"}

app = Flask(__name__)

@app.route('/api/submit', methods=['POST'])
def handler():
    data = request.get_json() or {}
    raw_text = data.get('user_input', '')
    tokens_list = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    if not tokens_list:
        return jsonify({"error": "No token entries parsed."}), 400
        
    try:
        r = requests.post(f"{BASE}/task/create", headers=HEADERS, json={"tool": "check", "tokens": tokens_list})
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

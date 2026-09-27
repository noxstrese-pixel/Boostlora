
import requests
from flask import Flask, request, jsonify

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5"}

app = Flask(__name__)

@app.route('/api/items', methods=['GET'])
def handler():
    job_id = request.args.get('job_id')
    after = request.args.get('after', 0)
    try:
        r = requests.get(f"{BASE}/task/items", headers=HEADERS, params={"job_id": job_id, "after": after})
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify

app = Flask(__name__)

SALTA7_BASE_URL = "https://salta7.store"
SALTA7_HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "Content-Type": "application/json"
}

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)

@app.route('/api/items', methods=['POST'])
def handle_items_checker():
    try:
        data = request.get_json() or {}
        raw_input = data.get('input', '')
        user_id = data.get('userId')

        if not user_id:
            return jsonify({"status": "error", "message": "Authentication required."}), 403

        lines_list = [line.strip() for line in raw_input.split('\n') if line.strip()]
        if not lines_list:
            return jsonify({"status": "success", "accounts": []}), 200

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance, role FROM users WHERE id = %s;", (user_id,))
        user_profile = cur.fetchone()
        
        if not user_profile:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "System account node missing."}), 404

        total_tokens = len(lines_list)
        cost_per_token = 0.01 
        total_cost = 0.00 if user_profile['role'] == 'admin' else (total_tokens * cost_per_token)
        current_balance = float(user_profile['balance'])

        if current_balance < total_cost:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": f"Insufficient funds. Required: ${total_cost:.2f} USD"}), 400

        payload = {"tool": "check", "tokens": lines_list}
        create_res = requests.post(f"{SALTA7_BASE_URL}/task/create", headers=SALTA7_HEADERS, json=payload, timeout=10)
        if create_res.status_code != 200:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "message": "Task initialization failed."}), 400
            
        job_id = create_res.json().get("job_id")
        if total_cost > 0:
            cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s;", (total_cost, user_id))
            conn.commit()
        cur.close()
        conn.close()

        results_collection = []
        max_attempts = 45  
        after_id = 0

        for attempt in range(max_attempts):
            poll_res = requests.get(f"{SALTA7_BASE_URL}/task/items", headers=SALTA7_HEADERS, params={"job_id": job_id, "after": after_id}, timeout=10)
            if poll_res.status_code != 200:
                time.sleep(1.0)
                continue
                
            poll_data = poll_res.json()
            for item in poll_data.get("results", []):
                nitro_label = f"Nitro ({item.get('nitro_days', 0)}d)" if item.get("nitro") else "No Nitro"
                phone_label = "✅ Linked" if item.get("has_phone") else "No Phone"
                results_collection.append({
                    "status": item.get("status", "invalid"),  
                    "username": item.get("username") or item.get("global_name") or "Unknown User",
                    "phone": phone_label,
                    "nitro": nitro_label,
                    "has_pfp": item.get("has_avatar", False)
                })

            after_id = poll_data.get("last_id", after_id)
            if poll_data.get("status") != "running":
                break
            time.sleep(1.0)  

        return jsonify({"status": "success", "accounts": results_collection}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"[Pipeline Error]: {str(e)}"}), 500

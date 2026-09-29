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

@app.route('/api/booster', methods=['POST'])
def handle_booster_pipeline():
    try:
        data = request.get_json() or {}
        invite_link = data.get('input', '')  
        boost_count = data.get('amount', '2')
        strategy_source = data.get('strategy', 'salta7') 
        custom_tokens_raw = data.get('custom_tokens', '')
        user_id = data.get('userId')

        if not invite_link:
            return jsonify({"status": "error", "logs": ["[Error] Missing target server invite code."]}), 200

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance, role FROM users WHERE id = %s;", (user_id,))
        user_profile = cur.fetchone()
        
        if not user_profile:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "logs": ["[Error] Session invalid. Please log in again."]}), 200

        total_boosts = int(boost_count) if boost_count else 2
        cost_per_boost = 0.18
        total_cost = 0.00 if user_profile['role'] == 'admin' else (total_boosts * cost_per_boost)
        current_balance = float(user_profile['balance'])

        if current_balance < total_cost:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "logs": [f"❌ [Insufficient Funds] Balance: ${current_balance:.2f} USD | Required: ${total_cost:.2f} USD"]}), 200

        payload = {"tool": "boost", "invite": invite_link}
        if strategy_source == "salta7":
            payload["mode"] = "stock"
            payload["boosts"] = total_boosts
            logs_initial = f"[System] Initializing Stock Boost Queue: Requesting {payload['boosts']} boosts..."
        else:
            payload["mode"] = "byot"
            tokens_list = [t.strip() for t in custom_tokens_raw.split('\n') if t.strip()]
            if not tokens_list:
                cur.close()
                conn.close()
                return jsonify({"status": "error", "logs": ["[Error] No custom tokens provided."]}), 200
            payload["tokens"] = tokens_list
            logs_initial = f"[System] Initializing BYOT Boost Queue: Dispatched {len(tokens_list)} profiles..."

        create_res = requests.post(f"{SALTA7_BASE_URL}/task/create", headers=SALTA7_HEADERS, json=payload, timeout=12)
        if create_res.status_code != 200:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "logs": ["❌ [Salta7 Validation Failure] Connection Refused"]}), 200

        job_id = create_res.json().get("job_id")
        if total_cost > 0:
            cur.execute("UPDATE users SET balance = balance - %s WHERE id = %s;", (total_cost, user_id))
            conn.commit()
        cur.close()
        conn.close()

        logs_output = [f"[Ledger] Deducted: ${total_cost:.2f} USD.", logs_initial, f"✅ [Task Started] Job ID: {job_id}"]
        max_polls = 30
        for attempt in range(max_polls):
            time.sleep(10.0 if attempt > 0 else 1.0)
            status_res = requests.get(f"{SALTA7_BASE_URL}/task/status", headers=SALTA7_HEADERS, params={"job_id": job_id}, timeout=10)
            if status_res.status_code != 200:
                continue
            job = status_res.json()
            delivered = job.get("boosts_delivered", 0)
            requested = job.get("boosts_requested", 0)
            job_status = job.get("status", "running")

            if strategy_source == "salta7":
                logs_output.append(f"⏳ [Fulfillment Update] Applied: {delivered} / {requested} shifts...")
            else:
                byot_metrics = job.get("byot") or {}
                logs_output.append(f"⏳ [BYOT Update] Accounts Joined: {delivered} | Applied: {byot_metrics.get('boosts_applied', 0)}")

            if job_status != "running":
                logs_output.append(f"🏆 [Finished] Pipeline exited with state: {job_status}")
                break
        return jsonify({"status": "success", "logs": logs_output}), 200
    except Exception as e:
        return jsonify({"status": "error", "logs": [f"[Fatal Error]: {str(e)}"]}), 500

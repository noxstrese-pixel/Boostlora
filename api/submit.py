import os
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- PREMIUM INTEGRATION PARAMETERS ---
SALTA7_BASE_URL = "https://salta7.store"
SALTA7_HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "Content-Type": "application/json"
}

ADMIN_ADDRESSES = {
    "BTC": "1YourBitcoinWalletAddressHere",
    "LTC": "LYourLitecoinWalletAddressHere",
    "DOGE": "DYourDogecoinWalletAddressHere",
    "SOL": "SYourSolanaWalletAddressHere"
}

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)


# =====================================================================
# 1. CORE AUTHENTICATION PIPELINES
# =====================================================================

@app.route('/api/submit/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()['count']
        role = 'admin' if count == 0 else 'user'
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Store username in the email database column cleanly
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s);",
            (username, hashed, role)
        )
        conn.commit()
        return jsonify({"message": f"Account created. Assigned role: {role}"}), 201
    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        return jsonify({"error": "Username already exists"}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/submit/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s;", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({
            "userId": user['id'],
            "username": user['email'],
            "role": user['role']
        }), 200
    return jsonify({"error": "Invalid login credentials"}), 401

@app.route('/api/submit/dashboard', methods=['GET'])
def dashboard():
    user_id = request.args.get('userId')
    role = request.args.get('role')
    
    if not user_id or user_id == "undefined":
        return jsonify({"error": "Authentication required"}), 403

    conn = get_db_connection()
    cur = conn.cursor()
    if role == 'admin':
        cur.execute("SELECT id, email, role, balance FROM users;")
        all_users = cur.fetchall()
        cur.execute("SELECT * FROM deposits ORDER BY created_at DESC;")
        all_deposits = cur.fetchall()
        cur.close()
        conn.close()
        for u in all_users:
            u['balance'] = float(u['balance'])
        for d in all_deposits:
            d['amount'] = float(d['amount'])
        return jsonify({"role": "admin", "users": all_users, "allDeposits": all_deposits})
        
    cur.execute("SELECT id, email, balance FROM users WHERE id = %s;", (user_id,))
    profile = cur.fetchone()
    cur.execute("SELECT * FROM deposits WHERE user_id = %s ORDER BY created_at DESC;", (user_id,))
    my_deposits = cur.fetchall()
    cur.close()
    conn.close()
    
    for d in my_deposits:
        d['amount'] = float(d['amount'])
    return jsonify({
        "role": "user",
        "balance": float(profile['balance']) if profile else 0.00,
        "myDeposits": my_deposits
    })


# =====================================================================
# 2. SALTA7 USER PIPELINES & WALLET DEDUCTION ENGINES
# =====================================================================

@app.route('/api/submit', methods=['POST'])
def handle_joiner_pipeline():
    try:
        data = request.get_json() or {}
        invite_code = data.get('input', '')  
        join_amount = data.get('amount', '50')
        custom_tokens_raw = data.get('custom_tokens', '')  
        user_id = data.get('userId')

        if not invite_code:
            return jsonify({"status": "error", "logs": ["[Error] Target server invite parameter code is missing."]}), 200

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT balance, role FROM users WHERE id = %s;", (user_id,))
        user_profile = cur.fetchone()
        
        if not user_profile:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "logs": ["[Error] System user node not found."]}), 200

        total_members = int(join_amount) if join_amount else 50
        cost_per_unit = 0.09
        total_cost = 0.00 if user_profile['role'] == 'admin' else (total_members * cost_per_unit)
        current_balance = float(user_profile['balance'])

        if current_balance < total_cost:
            cur.close()
            conn.close()
            return jsonify({"status": "error", "logs": [f"❌ [Insufficient Funds] Balance: ${current_balance:.2f} USD | Required: ${total_cost:.2f} USD"]}), 200

        payload = {"tool": "join", "invite": invite_code}
        tokens_list = [t.strip() for t in custom_tokens_raw.split('\n') if t.strip()] if custom_tokens_raw else []

        if tokens_list:
            payload["mode"] = "byot"
            payload["tokens"] = tokens_list
            logs_initial = f"[System] Initializing BYOT Joiner: Injecting {len(tokens_list)} custom profiles..."
        else:
            payload["mode"] = "stock"
            payload["product"] = "discord"  
            payload["quantity"] = total_members
            logs_initial = f"[System] Initializing Stock Joiner: Requesting {payload['quantity']} accounts..."

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
        max_polls = 10
        for attempt in range(max_polls):
            time.sleep(5.0 if attempt > 0 else 1.0)
            status_res = requests.get(f"{SALTA7_BASE_URL}/task/status", headers=SALTA7_HEADERS, params={"job_id": job_id}, timeout=10)
            if status_res.status_code != 200:
                continue
            job = status_res.json()
            delivered = job.get("boosts_delivered", 0)  
            requested = job.get("boosts_requested", 0)
            job_status = job.get("status", "running")

            if payload["mode"] == "byot":
                byot_metrics = job.get("byot") or {}
                logs_output.append(f"⏳ [BYOT Update] Submitted: {requested} | Joined: {byot_metrics.get('joined', delivered)}")
            else:
                logs_output.append(f"⏳ [Fulfillment Update] Allocations Processed: {delivered} / {requested}")

            if job_status != "running":
                logs_output.append(f"🏆 [Finished] Task state exited with parameter: {job_status}")
                break
        return jsonify({"status": "success", "logs": logs_output}), 200
    except Exception as e:
        return jsonify({"status": "error", "logs": [f"[Fatal Error]: {str(e)}"]}), 500

wsgi_app = app

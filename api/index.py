import os
import time
import random
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
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
        
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()['count']
        role = 'admin' if count == 0 else 'user'
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s);",
            (email, hashed, role)
        )
        conn.commit()
        return jsonify({"message": f"Account created. Assigned role: {role}"}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "User already exists"}), 400
    finally:
        cur.close()
        conn.close()

@app.route('/api/submit/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({
            "userId": user['id'],
            "email": user['email'],
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
max_attempts = 20
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
=====================================================================
3. ADMINISTRATIVE OVERRIDES & CRYPTO INVOICING
=====================================================================
@app.route('/api/booster/invoice', methods=['POST'])
def generate_invoice():
data = request.get_json() or {}
user_id = data.get('userId')
email = data.get('email')
coin = data.get('coin')
amount = data.get('amount')
if not coin or not amount or float(amount) <= 0:
return jsonify({"error": "Invalid deposit parameters"}), 400
invoice_id = f"TX-{random.randint(100000, 999999)}"
wallet = ADMIN_ADDRESSES.get(coin, "Address Unconfigured")
conn = get_db_connection()
cur = conn.cursor()
cur.execute(
"INSERT INTO deposits (id, user_id, user_email, coin, amount, wallet_address, status) VALUES (%s, %s, %s, %s, %s, %s, %s);",
(invoice_id, user_id, email, coin, float(amount), wallet, 'pending')
)
conn.commit()
cur.close()
conn.close()
return jsonify({
"invoiceId": invoice_id,
"coin": coin,
"amount": float(amount),
"address": wallet
}), 201
@app.route('/api/booster_status/credit', methods=['POST'])
def credit_user():
data = request.get_json() or {}
admin_role = data.get('adminRole')
target_user_id = data.get('targetUserId')
credit_amount = data.get('creditAmount')
deposit_id = data.get('depositId')
if admin_role != 'admin':
return jsonify({"error": "Administrative credentials required"}), 403
conn = get_db_connection()
cur = conn.cursor()
cur.execute("UPDATE users SET balance = balance + %s WHERE id = %s;", (float(credit_amount), target_user_id))
if deposit_id:
cur.execute("UPDATE deposits SET status = 'confirmed' WHERE id = %s;", (deposit_id,))
conn.commit()
cur.close()
conn.close()
return jsonify({"success": True, "message": "Funds credited successfully."})

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
    try:
        data = request.get_json(force=True) or {}
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
            
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Pull count to check if this user becomes admin or standard user
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()['count']
        role = 'admin' if count == 0 else 'user'
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Inject custom username safely inside your database schema setup
        cur.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s);",
            (username, hashed, role)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": f"Account created. Assigned role: {role}"}), 201
        
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"error": f"Server Core Error: {str(e)}"}), 500

@app.route('/api/submit/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True) or {}
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
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"Server Core Error: {str(e)}"}), 500

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
    
    if my_deposits:
        for d in my_deposits:
            d['amount'] = float(d['amount'])
    return jsonify({
        "role": "user",
        "balance": float(profile['balance']) if profile else 0.00,
        "myDeposits": my_deposits
    })

@app.route('/api/submit', methods=['POST'])
def handle_joiner_pipeline():
    return jsonify({"status": "disabled", "logs": ["Main server routine initialization pending."]}), 200

wsgi_app = app

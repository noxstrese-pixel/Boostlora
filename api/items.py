import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def parse_discord_token_profile(token):
    """
    Queries the official Discord API to fetch true user profile indicators.
    Returns status parameters structured specifically for Salta7 UI rendering rules.
    """
    headers = {
        "Authorization": token.strip(),
        "Content-Type": "application/json"
    }
    try:
        # Check standard user record parameters
        user_res = requests.get("https://discord.com", headers=headers, timeout=4)
        
        # Capture standard system flags indicating suspension / locks
        if user_res.status_code == 403:
            return {"status": "locked", "username": "Locked Account", "phone": "Unknown", "nitro": "No Nitro", "has_pfp": False}
        if user_res.status_code != 200:
            return {"status": "invalid", "username": token.strip()[:14] + "...", "phone": "Unknown", "nitro": "No Nitro", "has_pfp": False}
            
        user_data = user_res.json()
        
        # Check for premium Nitro sub-billing indicators
        nitro_res = requests.get("https://discord.com/billing/subscriptions", headers=headers, timeout=4)
        nitro_status = "No Nitro"
        if nitro_res.status_code == 200 and len(nitro_res.json()) > 0:
            nitro_status = "Nitro Active"

        username = user_data.get("username", "Unknown User")
        phone_number = user_data.get("phone") or "No Phone"
        avatar_hash = user_data.get("avatar")
        
        return {
            "status": "valid",
            "username": username,
            "phone": phone_number,
            "nitro": nitro_status,
            "has_pfp": True if avatar_hash else False
        }
    except Exception:
        # Fallback tracking indicator if endpoint times out or drops
        return {"status": "invalid", "username": "Connection Error", "phone": "Unknown", "nitro": "No Nitro", "has_pfp": False}

@app.route('/api/items', methods=['POST'])
def handle_items_checker():
    try:
        data = request.get_json() or {}
        raw_input = data.get('input', '')
        tokens_list = [t.strip() for t in raw_input.split('\n') if t.strip()]

        accounts_results_array = []

        for token in tokens_list:
            if not token:
                continue
            
            # Fetch profile parameters directly from Discord
            profile_data = parse_discord_token_profile(token)
            accounts_results_array.append(profile_data)
            
            time.sleep(0.15) # Protects proxies from slamming rate-limit gates

        # Return a structured collection object array directly down to the UI engine grid
        return jsonify({
            "status": "success",
            "accounts": accounts_results_array
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"[Fatal Pipeline Crash] Server error: {str(e)}"
        }), 500

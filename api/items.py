import json
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def fetch_discord_profile(token):
    """
    Connects to the Discord User API to check token validity 
    and grab profile data (Nitro, Phone, PFP, and badges).
    """
    headers = {
        "Authorization": token.strip(),
        "Content-Type": "application/json"
    }
    try:
        # Fetch standard profile configurations
        user_res = requests.get("https://discord.com", headers=headers, timeout=5)
        if user_res.status_code != 200:
            return {"valid": False}
        
        user_data = user_res.json()
        
        # Check for Nitro membership data maps
        nitro_res = requests.get("https://discord.com/billing/subscriptions", headers=headers, timeout=5)
        has_nitro = "No Nitro"
        if nitro_res.status_code == 200:
            if len(nitro_res.json()) > 0:
                has_nitro = "💎 Active Nitro"

        # Map out individual parameter fields nicely
        username = user_data.get("username", "Unknown")
        phone = user_data.get("phone") or "❌ No Phone"
        email_verified = "✅ Verified" if user_data.get("verified") else "❌ Unverified"
        avatar_hash = user_data.get("avatar")
        has_pfp = "✅ Has PFP" if avatar_hash else "❌ No PFP"
        
        return {
            "valid": True,
            "username": username,
            "phone": phone,
            "nitro": has_nitro,
            "pfp": has_pfp,
            "email": email_verified
        }
    except Exception:
        return {"valid": False}

@app.route('/api/items', methods=['POST'])
def handle_items_checker():
    try:
        data = request.get_json() or {}
        raw_input = data.get('input', '')
        tokens_list = [t for t in raw_input.split('\n') if t.strip()]

        logs_output = [
            f"[System] Initializing Full Capture Protocol for {len(tokens_list)} credentials..."
        ]

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
                
            clean_token = token.strip()[:15] + "..."
            logs_output.append(f"[Checking Account {index}] Contacting Discord databases...")
            
            # Query Discord profile status live
            profile = fetch_discord_profile(token)
            
            if not profile["valid"]:
                logs_output.append(f"❌ [Invalid Account] {clean_token} failed authorization tests.")
            else:
                # Beautiful inline dashboard output matrix reporting variables back
                report = f"✨ <b>[Valid]</b> User: <span style='color:#fff;'>{profile['username']}</span> | " \
                         f"Premium: <span style='color:#c084fc;'>{profile['nitro']}</span> | " \
                         f"PFP: <span style='color:#38bdf8;'>{profile['pfp']}</span> | " \
                         f"Phone: <span style='color:#fbbf24;'>{profile['phone']}</span> | " \
                         f"Email: {profile['email']}"
                logs_output.append(report)
                
            time.sleep(0.2) # Soft delay to protect endpoints from heavy API rate limits

        return jsonify({"status": "success", "logs": logs_output}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"[Fatal Error] Core pipeline failure: {str(e)}"}), 500

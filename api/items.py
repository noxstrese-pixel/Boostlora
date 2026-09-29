import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Real production mapping extracted directly from the user dashboard settings
SALTA7_BASE_URL = "https://salta7.store"
SALTA7_HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "Content-Type": "application/json"
}

@app.route('/api/items', methods=['POST'])
def handle_items_checker():
    try:
        data = request.get_json() or {}
        raw_input = data.get('input', '')
        
        # Parse pasted string rows line-by-line into clean array elements
        lines_list = [line.strip() for line in raw_input.split('\n') if line.strip()]

        if not lines_list:
            return jsonify({"status": "success", "accounts": []}), 200

        # --- STEP 1: INITIALIZE THE ASYNCHRONOUS CHECK RUN WITH SALTA7 ---
        payload = {
            "tool": "check",
            "tokens": lines_list
        }
        
        create_res = requests.post(
            f"{SALTA7_BASE_URL}/task/create", 
            headers=SALTA7_HEADERS, 
            json=payload, 
            timeout=10
        )
        
        if create_res.status_code != 200:
            return jsonify({
                "status": "error", 
                "message": f"Salta7 Task Initialization Failed (Status Code: {create_res.status_code})"
            }), 400
            
        task_data = create_res.json()
        job_id = task_data.get("job_id")
        
        if not job_id:
            return jsonify({"status": "error", "message": "No job identifier token returned from Salta7 API layer."}), 500

        # --- STEP 2: POLL THE REAL-TIME RESULTS CHANNEL ---
        results_collection = []
        max_attempts = 45  # Safety timeout loop boundaries protecting serverless instance lifecycle bounds
        after_id = 0

        for attempt in range(max_attempts):
            poll_params = {
                "job_id": job_id,
                "after": after_id
            }
            
            poll_res = requests.get(
                f"{SALTA7_BASE_URL}/task/items", 
                headers=SALTA7_HEADERS, 
                params=poll_params, 
                timeout=10
            )
            
            if poll_res.status_code != 200:
                time.sleep(1.0)
                continue
                
            poll_data = poll_res.json()
            
            # Map out each incremental status payload cleanly to populate your index.html display grid
            for item in poll_data.get("results", []):
                has_nitro = item.get("nitro", False)
                nitro_days = item.get("nitro_days", 0)
                nitro_label = f"Nitro ({nitro_days}d)" if has_nitro else "No Nitro"
                
                phone_label = "✅ Linked" if item.get("has_phone") else "No Phone"
                
                results_collection.append({
                    "status": item.get("status", "invalid"),  # valid, locked, invalid, error
                    "username": item.get("username") or item.get("global_name") or "Unknown User",
                    "phone": phone_label,
                    "nitro": nitro_label,
                    "has_pfp": item.get("has_avatar", False)
                })

            after_id = poll_data.get("last_id", after_id)
            
            # Instantly terminate the loop container when execution changes status parameters from running
            if poll_data.get("status") != "running":
                break
                
            time.sleep(1.0)  # Polling interval frequency rule requested by Salta7 engine rules

        return jsonify({
            "status": "success",
            "accounts": results_collection
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"[Pipeline Error] Salta7 processing failed: {str(e)}"
        }), 500

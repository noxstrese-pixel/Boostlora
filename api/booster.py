import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Production routing parameters mapped straight from your Salta7 portal instructions
SALTA7_BASE_URL = "https://salta7.store"
SALTA7_HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "Content-Type": "application/json"
}

@app.route('/api/booster', methods=['POST'])
def handle_booster_pipeline():
    try:
        data = request.get_json() or {}
        invite_link = data.get('input', '')  # Comes from input text layout box
        boost_count = data.get('amount', '2')
        strategy_source = data.get('strategy', 'salta7') # salta7 (stock) or custom (byot)
        custom_tokens_raw = data.get('custom_tokens', '')

        if not invite_link:
            return jsonify({"status": "error", "logs": ["[Error] Missing target server invite link or code."]}), 200

        # --- STEP 1: PARSE PAYLOAD CONFIGURATIONS BY SELECTED STRATEGY SOURCE ---
        payload = {
            "tool": "boost",
            "invite": invite_link
        }

        if strategy_source == "salta7":
            # Stock Mode Configuration
            payload["mode"] = "stock"
            payload["boosts"] = int(boost_count) if boost_count else 2
            logs_initial = f"[System] Initializing Stock Boost Queue: Requesting {payload['boosts']} boosts for invite code '{invite_link}'..."
        else:
            # Provide Your Own Tokens (BYOT) Mode Configuration
            payload["mode"] = "byot"
            # Separate pasted raw text block by line breaks into array fields
            tokens_list = [t.strip() for t in custom_tokens_raw.split('\n') if t.strip()]
            if not tokens_list:
                return jsonify({"status": "error", "logs": ["[Error] Custom strategy selected, but no tokens were provided in the field input."]}), 200
            
            payload["tokens"] = tokens_list
            logs_initial = f"[System] Initializing BYOT Custom Boost Queue: Dispatched {len(tokens_list)} token profiles for invite '{invite_link}'..."

        # --- STEP 2: DISPATCH THE RUNNER REQUEST TO SALTA7 GATES ---
        create_res = requests.post(
            f"{SALTA7_BASE_URL}/task/create",
            headers=SALTA7_HEADERS,
            json=payload,
            timeout=12
        )

        if create_res.status_code != 200:
            error_data = create_res.json() if create_res.status_code in [400, 403, 409] else {}
            error_msg = error_data.get("detail", f"HTTP Connection Refused (Code {create_res.status_code})")
            return jsonify({
                "status": "error",
                "logs": [f"❌ [Salta7 Validation Failure] {error_msg}"]
            }), 200

        job_data = create_res.json()
        job_id = job_data.get("job_id")

        if not job_id:
            return jsonify({"status": "error", "logs": ["[Error] Salta7 instance failed to return a valid tracking job_id."]}), 200

        # --- STEP 3: POLL STATUS CHANNELS TO RENDER OUTPUT LOGS ---
        logs_output = [logs_initial, f"✅ [Task Started] Unique tracking token mapped: {job_id}"]
        max_polls = 30
        
        for attempt in range(max_polls):
            # Short incremental delay between poll validation ticks (Recommended 10s by API documentation)
            time.sleep(10.0 if attempt > 0 else 1.0)

            status_res = requests.get(
                f"{SALTA7_BASE_URL}/task/status",
                headers=SALTA7_HEADERS,
                params={"job_id": job_id},
                timeout=10
            )

            if status_res.status_code != 200:
                continue

            job = status_res.json()
            delivered = job.get("boosts_delivered", 0)
            requested = job.get("boosts_requested", 0)
            job_status = job.get("status", "running")

            if strategy_source == "salta7":
                logs_output.append(f"⏳ [Fulfillment Update] Applied: {delivered} / {requested} server boosts safely inside guild corridors...")
            else:
                byot_metrics = job.get("byot") or {}
                applied_count = byot_metrics.get("boosts_applied", 0)
                logs_output.append(f"⏳ [BYOT Update] Accounts Joined: {delivered} | Total Applied Boosts: {applied_count}")

            if job_status != "running":
                if job_status == "completed":
                    logs_output.append("🏆 [Finished] Salta7 optimization pipeline completed your requested operations successfully!")
                else:
                    logs_output.append(f"⚠️ [Finished] Pipeline exited with final tracking state parameters: {job_status}")
                break

        return jsonify({"status": "success", "logs": logs_output}), 200

    except Exception as e:
        return jsonify({"status": "error", "logs": [f"[Fatal Error] Pipeline calculation failed: {str(e)}"]}), 500

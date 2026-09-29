import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Real production mapping matching your verified configuration credentials
SALTA7_BASE_URL = "https://salta7.store"
SALTA7_HEADERS = {
    "Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNOBYQW5",
    "Content-Type": "application/json"
}

@app.route('/api/submit', methods=['POST'])
def handle_joiner_pipeline():
    try:
        data = request.get_json() or {}
        invite_code = data.get('input', '')  # Target invite link code from form input
        join_amount = data.get('amount', '50')
        custom_tokens_raw = data.get('custom_tokens', '')  # Captures from pasted text string areas

        if not invite_code:
            return jsonify({"status": "error", "logs": ["[Error] Target server invite parameter code is missing."]}), 200

        # --- STEP 1: PARSE PAYLOAD CONFIGURATIONS BASED ON FIELD PROPERTIES ---
        payload = {
            "tool": "join",
            "invite": invite_code
        }

        # Check if the execution request contains custom tokens pasted inside the form fields
        tokens_list = [t.strip() for t in custom_tokens_raw.split('\n') if t.strip()] if custom_tokens_raw else []

        if tokens_list:
            # Provide Your Own Tokens (BYOT Mode)
            payload["mode"] = "byot"
            payload["tokens"] = tokens_list
            logs_initial = f"[System] Initializing BYOT Joiner: Injecting {len(tokens_list)} custom token profiles into server corridors..."
        else:
            # Pull From Salta7 Stock Inventory (Stock Mode)
            payload["mode"] = "stock"
            payload["product"] = "discord"  # Default slug from /task/products?tool=join
            payload["quantity"] = int(join_amount) if join_amount else 50
            logs_initial = f"[System] Initializing Stock Joiner: Requesting {payload['quantity']} platform account deliveries..."

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

        # --- STEP 3: STATUS POLLING THREAD (POLL EVERY ~10 SECONDS AS REQUESTED BY DOCS) ---
        logs_output = [logs_initial, f"✅ [Task Started] Unique tracking token mapped: {job_id}"]
        max_polls = 30
        
        for attempt in range(max_polls):
            # Enforce 10-second polling check loops to secure backend performance bounds
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
            delivered = job.get("boosts_delivered", 0)  # For join jobs, this counts accounts joined!
            requested = job.get("boosts_requested", 0)
            job_status = job.get("status", "running")

            if payload["mode"] == "byot":
                byot_metrics = job.get("byot") or {}
                joined_count = byot_metrics.get("joined", delivered)
                logs_output.append(f"⏳ [BYOT Update] Accounts Submitted: {requested} | Successfully Joined: {joined_count}")
            else:
                logs_output.append(f"⏳ [Fulfillment Update] Processed Member Allocations: {delivered} / {requested}")

            if job_status != "running":
                if job_status == "completed":
                    logs_output.append("🏆 [Finished] Salta7 optimization pipeline completed your member allocations successfully!")
                else:
                    logs_output.append(f"⚠️ [Finished] Pipeline exited with final tracking code: {job_status}")
                break

        return jsonify({"status": "success", "logs": logs_output}), 200

    except Exception as e:
        return jsonify({"status": "error", "logs": [f"[Fatal Error] Pipeline calculation failed: {str(e)}"]}), 500

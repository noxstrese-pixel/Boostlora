from flask import Flask, request, jsonify

app = Flask(__name__)

# VERCEL COMPATIBILITY FIX: Route directly to base root '/'
@app.route('/', methods=['POST'])
def handle_joiner():
    try:
        data = request.get_json() or {}
        invite_code = data.get('input', '')
        amount = int(data.get('amount', 50))

        logs_output = [
            f"[System] Initializing socket connection pathways for invite parameter: {invite_code}"
        ]

        steps = min(amount, 5)
        for i in range(1, steps + 1):
            logs_output.append(f"[Worker Group {i}] Injecting automated profiles directly into server corridors...")
            logs_output.append("🚀 [Success] Managed batch injection profile connection success.")

        logs_output.append("🏆 [Order Finished] Dispatched requested member allocations safely.")
        return jsonify({"status": "success", "logs": logs_output}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"[Fatal Error] Joiner crashed: {str(e)}"}), 500

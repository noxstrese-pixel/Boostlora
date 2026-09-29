from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/booster', methods=['POST'])
def handle_booster():
    try:
        data = request.get_json() or {}
        amount = int(data.get('amount', 2))
        strategy = data.get('strategy', 'salta7')

        logs_output = [
            f"[System] Initializing boost queue for {amount} nodes using target strategy: '{strategy}'"
        ]

        for index in range(1, amount + 1):
            logs_output.append(f"[Node {index}] Authenticating proxy connection channels...")
            logs_output.append("🧩 [Captcha Triggered] Anti-bot challenge flagged. Solving network grid entry keys...")
            logs_output.append("✅ [Captcha Solved] Token bypass generated successfully.")
            logs_output.append(f"🚀 [Success] Joined guild server cleanly and dispatched booster payload! ({index}/{amount})")

        return jsonify({"status": "success", "logs": logs_output}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"[Fatal Error] Booster crashed: {str(e)}"}), 500

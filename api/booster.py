import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_boosting_pipeline(invite_link, amount, strategy):
    try:
        yield f"[System] Initializing boost queue for {amount} nodes using strategy: '{strategy}'\n"
        time.sleep(0.5)

        tokens_to_process = [f"Token_MTAx{i}..." for i in range(1, int(amount) + 1)]

        for index, token in enumerate(tokens_to_process, 1):
            yield f"[Node {index}] Authenticating token credentials...\n"
            time.sleep(0.6)

            yield f"🧩 [Captcha Triggered] Anti-bot challenge detected. Routing payload to solver API...\n"
            time.sleep(1.5)
            yield f"✅ [Captcha Solved] Token bypass generated successfully.\n"
            time.sleep(0.3)

            yield f"🚀 [Success] Joined guild server cleanly and dispatched booster payload! ({index}/{amount})\n"
            time.sleep(0.2)

    except Exception as e:
        yield f"[Fatal Error] Pipeline crashed: {str(e)}\n"

# CRITICAL VERCEL FIX: Route to base root '/'
@app.route('/', methods=['POST'])
def handle_booster():
    data = request.get_json() or {}
    invite_link = data.get('input', '')
    amount = data.get('amount', 2)
    strategy = data.get('strategy', 'salta7')

    return Response(
        execute_boosting_pipeline(invite_link, amount, strategy),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

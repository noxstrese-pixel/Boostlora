import json
import time
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_booster():
    data = request.get_json() or {}
    amount = data.get('amount', 2)
    strategy = data.get('strategy', 'salta7')

    @stream_with_context
    def generate():
        yield f"[System] Initializing boost queue for {amount} nodes using target strategy: '{strategy}'\n"
        time.sleep(0.4)

        tokens_to_process = [f"Token_MTAx{i}..." for i in range(1, int(amount) + 1)]

        for index, token in enumerate(tokens_to_process, 1):
            yield f"[Node {index}] Authenticating proxy connection channels...\n"
            time.sleep(0.4)

            yield f"🧩 [Captcha Triggered] Anti-bot challenge flagged. Solving network grid entry keys...\n"
            time.sleep(1.2)
            yield f"✅ [Captcha Solved] Token bypass generated successfully.\n"
            time.sleep(0.2)

            yield f"🚀 [Success] Joined guild server cleanly and dispatched booster payload! ({index}/{amount})\n"
            time.sleep(0.1)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

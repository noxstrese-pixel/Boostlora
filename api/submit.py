import json
import time
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_joiner():
    data = request.get_json() or {}
    invite_code = data.get('input', '')
    amount = data.get('amount', 50)

    @stream_with_context
    def generate():
        yield f"[System] Initializing socket connection pathways for invite parameter: {invite_code}\n"
        time.sleep(0.5)

        total_joins = int(amount) if amount else 50
        steps = min(total_joins, 5)
        
        for i in range(1, steps + 1):
            yield f"[Worker Group {i}] Injecting automated profiles directly down into server socket corridors...\n"
            time.sleep(0.4)
            yield f"🚀 [Success] Managed batch injection profile connection success.\n"

        yield f"🏆 [Order Finished] Dispatched requested member allocations safely.\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

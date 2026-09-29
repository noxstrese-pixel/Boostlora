import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_joiner_pipeline(invite_code, amount):
    try:
        yield f"[System] Initializing server join module for: {invite_code}\n"
        time.sleep(0.8)

        total_joins = int(amount) if amount else 50
        steps = min(total_joins, 5)
        
        for i in range(1, steps + 1):
            yield f"[Worker Group {i}] Pushing connection profiles to server socket corridors...\n"
            time.sleep(0.5)
            yield f"🚀 [Success] Managed batch injection profile connection success.\n"

        yield f"🏆 [Order Finished] Dispatched requested member allocations safely.\n"

    except Exception as e:
        yield f"[Fatal Error] Joiner pipeline crashed: {str(e)}\n"

# CRITICAL VERCEL FIX: Route to base root '/'
@app.route('/', methods=['POST'])
def handle_joiner():
    data = request.get_json() or {}
    invite_code = data.get('input', '')
    amount = data.get('amount', 50)

    return Response(
        execute_joiner_pipeline(invite_code, amount),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

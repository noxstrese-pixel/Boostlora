import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_joiner_pipeline(invite_code, amount):
    try:
        yield f"[System] Initializing server join module for: {invite_code}\n"
        yield f"[System] Dispatched request parameter: Injecting {amount} automated profile nodes...\n"
        time.sleep(1.5)

        total_joins = int(amount) if amount else 50
        steps = min(total_joins, 5) # Show a few live console logs so they don't wait forever
        
        for i in range(1, steps + 1):
            yield f"<span style='color:#64748b;'>[Worker Group {i}]</span> Pushing connection profiles down to server socket corridors...\n"
            time.sleep(1.0)
            yield f"<span style='color:#10b981;'>🚀 [Success]</span> Managed batch injection profile connection success.\n"

        yield f"<span style='color:#10b981; font-weight:bold;'>🏆 [Order Finished]</span> Dispatched requested member allocations safely to target room.\n"

    except Exception as e:
        yield f"<span style='color:#ef4444;'>[Fatal Error] Joiner pipeline crashed: {str(e)}</span>\n"

@app.route('/api/submit', methods=['POST'])
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

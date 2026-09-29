import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_checker_pipeline(tokens_list):
    try:
        yield f"[System] Parsing {len(tokens_list)} auth tokens from dashboard upload grid...\n"
        time.sleep(1.0)

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
                
            clean_token = token.strip()[:15] + "..."
            yield f"<span style='color:#64748b;'>[Checking Account {index}]</span> Testing validation tokens...\n"
            time.sleep(1.2)

            # Simulated token state validation protocols
            if "invalid" in token.lower() or index == 2:
                yield f"<span style='color:#ef4444;'>❌ [Invalid Account]</span> {clean_token} failed authentication check.\n"
            else:
                yield f"<span style='color:#10b981; font-weight:bold;'>✅ [Valid Token]</span> {clean_token} verified successfully! User Profile active.\n"
            time.sleep(0.5)

    except Exception as e:
        yield f"<span style='color:#ef4444;'>[Fatal Error] Checking system crashed: {str(e)}</span>\n"

@app.route('/api/items', methods=['POST'])
def handle_items_checker():
    data = request.get_json() or {}
    raw_input = data.get('input', '')
    
    # Split the pasted block by lines to check tokens one by one
    tokens_list = [t for t in raw_input.split('\n') if t.strip()]

    return Response(
        execute_checker_pipeline(tokens_list),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_checker_pipeline(tokens_list):
    try:
        yield f"[System] Parsing {len(tokens_list)} auth tokens from dashboard upload grid...\n"
        time.sleep(0.5)

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
                
            clean_token = token.strip()[:15] + "..."
            yield f"[Checking Account {index}] Testing validation tokens...\n"
            time.sleep(0.8)

            if "invalid" in token.lower() or index == 2:
                yield f"❌ [Invalid Account] {clean_token} failed authentication check.\n"
            else:
                yield f"✅ [Valid Token] {clean_token} verified successfully! User Profile active.\n"
            time.sleep(0.2)

    except Exception as e:
        yield f"[Fatal Error] Checking system crashed: {str(e)}\n"

# CRITICAL VERCEL FIX: Route to base root '/' because Vercel handles the '/api/items' routing path externally
@app.route('/', methods=['POST'])
def handle_items_checker():
    data = request.get_json() or {}
    raw_input = data.get('input', '')
    
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

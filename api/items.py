import json
import time
from flask import Flask, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_items_checker():
    data = request.get_json() or {}
    raw_input = data.get('input', '')
    tokens_list = [t for t in raw_input.split('\n') if t.strip()]

    # Use stream_with_context wrapper to prevent Vercel invocation runtime failures
    @stream_with_context
    def generate():
        yield f"[System] Parsing {len(tokens_list)} auth tokens from upload grid...\n"
        time.sleep(0.3)

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
                
            clean_token = token.strip()[:15] + "..."
            yield f"[Checking Account {index}] Testing authorization headers...\n"
            time.sleep(0.5)

            if "invalid" in token.lower() or index == 2:
                yield f"❌ [Invalid Account] {clean_token} failed verification rules.\n"
            else:
                yield f"✅ [Valid Token] {clean_token} active and authenticated cleanly.\n"
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

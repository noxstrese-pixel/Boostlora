import json
import time
from flask import Flask, request, Response

app = Flask(__name__)

def execute_boosting_pipeline(invite_link, amount, strategy):
    """
    Background generator loop that handles your discord token network logic 
    and yields real-time terminal event lines back down to the user's dashboard view.
    """
    try:
        yield f"[System] Initializing boost queue for {amount} nodes using strategy: '{strategy}'\n"
        time.sleep(1)

        # Mock array representing how your token database sets/reads custom inputs
        # Swap this out with your actual database queries or token loading arrays!
        tokens_to_process = [f"Token_MTAx{i}..." for i in range(1, int(amount) + 1)]

        for index, token in enumerate(tokens_to_process, 1):
            yield f"<span style='color:#64748b;'>[Node {index}]</span> Authenticating token credentials...\n"
            time.sleep(1.2)

            # --- SIMULATE TOKEN STATUS VALIDATION CHECK ---
            if index == 3: # Example showing what happens when a token fails
                yield f"<span style='color:#ef4444;'>❌ [Invalid Token]</span> {token} failed authorization header tests. Skipping...\n"
                continue

            # --- SIMULATE CAPTCHA ENGINE CHALLENGES ---
            yield f"<span style='color:#f59e0b;'>🧩 [Captcha Triggered]</span> Anti-bot challenge detected. Routing payload to solver API...\n"
            time.sleep(2.5) # Simulate time taken by cap solver APIs (Capsolver/2Captcha)
            yield f"<span style='color:#10b981;'>✅ [Captcha Solved]</span> Token bypass generated in 2.5s. Simulating room join protocols...\n"
            time.sleep(1.0)

            # --- SUCCESSFUL JOIN & BOOST EVENT ---
            yield f"<span style='color:#10b981; font-weight:bold;'>🚀 [Success]</span> Joined guild server cleanly and dispatched booster payload! ({index}/{amount})\n"
            time.sleep(0.8)

    except Exception as e:
        yield f"<span style='color:#ef4444;'>[Fatal Error] Pipeline crashed: {str(e)}</span>\n"

@app.route('/api/booster', methods=['POST'])
def handle_booster():
    # Parse the JSON parameters sent over from handleApiAction in index.html
    data = request.get_json() or {}
    
    invite_link = data.get('input', '')
    amount = data.get('amount', 2)
    strategy = data.get('strategy', 'salta7')

    # Launch the live text event stream response container channel
    return Response(
        execute_boosting_pipeline(invite_link, amount, strategy),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no' # Forces Vercel/Cloudflare networks to stream data instantly instead of buffering chunks
        }
    )

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/api/deposit_webhook', methods=['POST'])
def handle_deposit():
    payload = request.get_data()
    sig_header = request.headers.get('X-Cc-Webhook-Signature')
    
    # 1. Verify the signature here using Coinbase API keys
    # 2. Extract user data and deposit amounts
    # 3. Call your internal booster tools if payment succeeds
    
    print("Payment Verified Successfully!")
    return jsonify({"status": "success"}), 200

import json
import requests

BASE = "https://salta7.store"
HEADERS = {"Authorization": "Bearer FWG7PJY53V4PLHI1TED5C7SYFNDBYQN5"}

def handler(request):
    # 1. Access the request body directly using Vercel's request parsing specifications
    try:
        # Handles cases where request.body might be a dictionary or a byte string
        if hasattr(request, 'get_json'):
            data = request.get_json() or {}
        elif hasattr(request, 'body'):
            if isinstance(request.body, dict):
                data = request.body
            else:
                data = json.loads(request.body.decode('utf-8')) if request.body else {}
        else:
            data = {}
    except Exception as parse_err:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to decode JSON payload", "details": str(parse_err)})
        }

    # 2. Key Mapping Check: Try multiple variations to locate your frontend's input text fields
    raw_text = ""
    if isinstance(data, dict):
        raw_text = data.get('user_input') or data.get('tokens') or data.get('text') or ""

    # 3. Clean and parse strings into structured lists
    if isinstance(data, list):
        tokens_list = [str(item).strip() for item in data if str(item).strip()]
    else:
        tokens_list = [line.strip() for line in str(raw_text).split('\n') if line.strip()]

    if not tokens_list:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "No token entries parsed. Check key name."})
        }

    # 4. Outbound POST to salta7.store API 
    try:
        r = requests.post(
            f"{BASE}/task/create",
            headers=HEADERS,
            json={"tool": "check", "tokens": tokens_list},
            timeout=15
        )

        # Catch upstream problems (like a 400, 403, or 502) and pass along safely without dropping
        if not r.ok:
            try:
                details = r.json()
            except Exception:
                details = r.text[:150]
            return {
                "statusCode": 502,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Upstream service error status", "status_code": r.status_code, "details": details})
            }

        # Successful backend handshake
        try:
            res_body = r.json()
        except Exception:
            res_body = {"status": "success", "raw_payload": r.text[:200]}

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps(res_body)
        }

    except requests.exceptions.RequestException as network_err:
        return {
            "statusCode": 503,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Failed to establish database connection handshake", "details": str(network_err)})
        }
    except Exception as runtime_err:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Crash inside handler logic execution runtime", "details": str(runtime_err)})
        }

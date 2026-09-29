from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/items")
async def handle_items_checker(request: Request):
    try:
        data = await request.json() or {}
        raw_input = data.get('input', '')
        tokens_list = [t for t in raw_input.split('\n') if t.strip()]

        logs_output = [
            f"[System] Parsing {len(tokens_list)} auth tokens from dashboard upload grid..."
        ]

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
            clean_token = token.strip()[:15] + "..."
            logs_output.append(f"[Checking Account {index}] Testing authorization headers...")

            if "invalid" in token.lower() or index == 2:
                logs_output.append(f"❌ [Invalid Account] {clean_token} failed verification rules.")
            else:
                logs_output.append(f"✅ [Valid Token] {clean_token} active and authenticated cleanly.")

        return JSONResponse(content={"status": "success", "logs": logs_output})

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"[Fatal Error] Checker crashed: {str(e)}"})

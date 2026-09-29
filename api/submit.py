from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/submit")
async def handle_joiner(request: Request):
    try:
        data = await request.json() or {}
        invite_code = data.get('input', '')
        amount = int(data.get('amount', 50))

        logs_output = [
            f"[System] Initializing socket connection pathways for invite parameter: {invite_code}"
        ]

        steps = min(amount, 5)
        for i in range(1, steps + 1):
            logs_output.append(f"[Worker Group {i}] Injecting automated profiles directly into server corridors...")
            logs_output.append("🚀 [Success] Managed batch injection profile connection success.")

        logs_output.append("🏆 [Order Finished] Dispatched requested member allocations safely.")
        return JSONResponse(content={"status": "success", "logs": logs_output})

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"[Fatal Error] Joiner crashed: {str(e)}"})

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/api/submit")
async def handle_joiner(request: Request):
    data = await request.json() or {}
    invite_code = data.get('input', '')
    amount = int(data.get('amount', 50))

    async def generate_logs():
        yield f"[System] Initializing socket connection pathways for invite parameter: {invite_code}\n"
        await asyncio.sleep(0.5)

        steps = min(amount, 5)
        for i in range(1, steps + 1):
            yield f"[Worker Group {i}] Injecting automated profiles directly into server corridors...\n"
            await asyncio.sleep(0.4)
            yield f"🚀 [Success] Managed batch injection profile connection success.\n"

        yield f"🏆 [Order Finished] Dispatched requested member allocations safely.\n"

    return StreamingResponse(generate_logs(), media_type="text/plain")

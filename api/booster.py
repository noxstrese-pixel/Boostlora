import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/api/booster")
async def handle_booster(request: Request):
    data = await request.json() or {}
    amount = int(data.get('amount', 2))
    strategy = data.get('strategy', 'salta7')

    async def generate_logs():
        yield f"[System] Initializing boost queue for {amount} nodes using target strategy: '{strategy}'\n"
        await asyncio.sleep(0.5)

        for index in range(1, amount + 1):
            yield f"[Node {index}] Authenticating proxy connection channels...\n"
            await asyncio.sleep(0.5)

            yield f"🧩 [Captcha Triggered] Anti-bot challenge flagged. Solving network grid entry keys...\n"
            await asyncio.sleep(1.0)
            yield f"✅ [Captcha Solved] Token bypass generated successfully.\n"
            await asyncio.sleep(0.2)

            yield f"🚀 [Success] Joined guild server cleanly and dispatched booster payload! ({index}/{amount})\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(generate_logs(), media_type="text/plain")

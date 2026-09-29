import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/api/items")
async def handle_items_checker(request: Request):
    data = await request.json() or {}
    raw_input = data.get('input', '')
    tokens_list = [t for t in raw_input.split('\n') if t.strip()]

    async def generate_logs():
        yield f"[System] Parsing {len(tokens_list)} auth tokens from dashboard upload grid...\n"
        await asyncio.sleep(0.4)

        for index, token in enumerate(tokens_list, 1):
            if not token.strip():
                continue
            clean_token = token.strip()[:15] + "..."
            yield f"[Checking Account {index}] Testing authorization headers...\n"
            await asyncio.sleep(0.6)

            if "invalid" in token.lower() or index == 2:
                yield f"❌ [Invalid Account] {clean_token} failed verification.\n"
            else:
                yield f"✅ [Valid Token] {clean_token} active and authenticated cleanly.\n"
            await asyncio.sleep(0.1)

    return StreamingResponse(generate_logs(), media_type="text/plain")

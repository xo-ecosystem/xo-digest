from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from xo_core.services.message_bottle import (
    publish_message,
    subscribe_events_sse,
    list_messages,
)
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from typing import Optional, AsyncIterator
from xo_core.services.rate_limit import allow_publish_per_ip


router = APIRouter(tags=["message-bottle"])


@router.get("/message-bottle")
def message_bottle_status():
    return {"status": "ok"}


class PublishIn(BaseModel):
    drop_id: str = Field(..., min_length=1, max_length=64)
    author: Optional[str] = Field(None, max_length=64)
    text: str = Field(..., min_length=1, max_length=4096)


@router.post("/message-bottle/publish")
async def message_bottle_publish(payload: PublishIn, request: Request):
    client_ip = request.client.host if request.client else "0.0.0.0"
    allowed, remaining, capacity, refill = await allow_publish_per_ip(
        drop_id=payload.drop_id, client_ip=client_ip, tokens=1
    )
    headers = {
        "X-RateLimit-Policy": f"token-bucket; cap={capacity}; rate={refill}/s",
        "X-RateLimit-Tokens": f"{remaining:.2f}",
    }
    if not allowed:
        headers["Retry-After"] = "1"
        return JSONResponse(
            {"ok": False, "error": "rate_limited"}, status_code=429, headers=headers
        )

    msg = await publish_message(
        drop_id=payload.drop_id,
        text=payload.text,
        author=payload.author or "anon",
    )
    return JSONResponse({"ok": True, "message": msg}, headers=headers)


@router.get("/message-bottle/stream", response_class=HTMLResponse)
async def message_bottle_stream_page():
    return HTMLResponse(
        """
<!doctype html><meta charset="utf-8">
<title>Message Bottle Stream</title>
<h1>Live Bottles</h1>
<ul id="feed"></ul>
<script>
 const ul = document.getElementById('feed');
 const es = new EventSource('/message-bottle/stream/sse');
 es.onmessage = (ev) => {
   try {
     const data = JSON.parse(ev.data);
     const li = document.createElement('li');
     li.textContent = `[${data.drop_id}] ${data.author}: ${data.text}`;
     ul.prepend(li);
   } catch (e) {}
 };
</script>"""
    )


@router.get("/message-bottle/stream/sse")
async def message_bottle_stream_sse(request: Request) -> StreamingResponse:
    async def gen() -> AsyncIterator[bytes]:
        async for item in subscribe_events_sse(request=request):
            yield b"data: " + item + b"\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/message-bottle/latest")
async def message_bottle_latest(limit: int = 20, drop_id: Optional[str] = None):
    return {"messages": await list_messages(limit=limit, drop_id=drop_id)}

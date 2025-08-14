import asyncio
from fastapi import APIRouter, Request, Header, HTTPException
from starlette.responses import StreamingResponse, JSONResponse

from xo_core.services.broadcast import get_redis_broadcast, publish_to_channel
from xo_core.services.rate_limit import allow_publish_per_ip


router = APIRouter(tags=["stream"])


@router.get("/stream/{drop_id}")
async def stream_drop(drop_id: str, request: Request):
    """SSE stream for a specific drop_id channel."""

    async def event_generator():
        redis = get_redis_broadcast()
        pubsub = redis.pubsub()
        channel = f"drop:{drop_id}"
        await pubsub.subscribe(channel)
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message.get("type") == "message":
                    data = message.get("data")
                    if isinstance(data, (bytes, bytearray)):
                        data = data.decode("utf-8", "ignore")
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.1)
        finally:
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            except Exception:
                pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/publish/{drop_id}")
async def publish_drop(
    drop_id: str, payload: dict, request: Request, x_api_key: str = Header(None)
):
    """Publish a message to a drop_id channel (rate-limited)."""
    client_ip = request.client.host if request.client else "unknown"
    xfwd = request.headers.get("x-forwarded-for")
    if xfwd:
        client_ip = xfwd.split(",")[0].strip()
    allowed, remaining, capacity, refill_rate = await allow_publish_per_ip(
        drop_id, client_ip, tokens=1
    )
    if not allowed:
        retry_after = int(1 / max(refill_rate, 0.0001))
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limit", "remaining": int(remaining)},
            headers={
                "X-RateLimit-Limit": str(int(capacity)),
                "X-RateLimit-Remaining": str(int(remaining)),
                "Retry-After": str(retry_after),
            },
        )

    required = (x_api_key or "").strip()
    if required != os.getenv("XO_PUBLISH_TOKEN", "SHARED_SECRET_TOKEN"):
        raise HTTPException(status_code=401, detail="unauthorized")
    await publish_to_channel(f"drop:{drop_id}", payload)
    return {
        "ok": True,
        "remaining": int(remaining),
        "capacity": int(capacity),
    }

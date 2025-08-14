import asyncio
import json
import os
from typing import List

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from redis import asyncio as redis
import contextlib
import random
from xo_core.utils.rate_limit_source import check_source_limit


router = APIRouter(tags=["color-wave"])

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL = os.getenv("XO_COLOR_WAVE_CHANNEL", "color_wave_updates")


class WaveSettings(BaseModel):
    fade_speed: float
    trail_length: int
    colors: List[str]


async def _get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


@router.get("/color-wave/stream")
async def stream_settings(request: Request):
    client = await _get_redis()
    pubsub = client.pubsub()
    await pubsub.subscribe(CHANNEL)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=15.0
                )
                if message and message.get("data"):
                    yield f"data: {message['data']}\n\n"
                else:
                    yield ":keep-alive\n\n"
        finally:
            with contextlib.suppress(Exception):
                await pubsub.unsubscribe(CHANNEL)
                await pubsub.close()
            with contextlib.suppress(Exception):
                await client.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/color-wave/update")
async def update_settings(payload: WaveSettings):
    msg = payload.json()
    client = await _get_redis()
    try:
        await client.publish(CHANNEL, msg)
        return {"ok": True, "channel": CHANNEL}
    finally:
        with contextlib.suppress(Exception):
            await client.close()


@router.post("/color-wave/update/test")
async def test_wave(token: str):
    """
    Fires a dummy color wave event via Redis for testing.
    Requires ?token=... for protection. Does not touch any UI.
    """
    shared_token = os.getenv("OPS_SHARED_TOKEN", "changeme")
    if token != shared_token:
        return {"error": "unauthorized"}

    dummy_wave = WaveSettings(
        fade_speed=1.2,
        trail_length=10,
        colors=["#FF0000", "#00FF00", "#0000FF"],
    )
    client = await _get_redis()
    try:
        await client.publish(CHANNEL, dummy_wave.json())
    finally:
        with contextlib.suppress(Exception):
            await client.close()
    return {"ok": True, "published": dummy_wave.dict()}


# Periodic heartbeat publisher (opt-in via env)
_heartbeat_task: asyncio.Task | None = None


async def _heartbeat_loop() -> None:
    client = await _get_redis()
    try:
        while True:
            wave = {
                "fade_speed": round(random.uniform(0.5, 1.5), 2),
                "trail_length": random.randint(5, 12),
                "colors": random.sample(
                    ["#FF0000", "#00FF00", "#0000FF", "#FFD700", "#FF69B4", "#1E90FF"],
                    k=3,
                ),
                "source": "heartbeat",
            }
            await client.publish(CHANNEL, json.dumps(wave))
            interval = int(os.getenv("COLOR_WAVE_HEARTBEAT_SEC", "30"))
            await asyncio.sleep(max(1, interval))
    finally:
        with contextlib.suppress(Exception):
            await client.close()


async def start_color_wave_heartbeat() -> None:
    global _heartbeat_task
    enabled = os.getenv("COLOR_WAVE_HEARTBEAT", "true").lower() == "true"
    if not enabled:
        return
    if _heartbeat_task is None or _heartbeat_task.done():
        _heartbeat_task = asyncio.create_task(_heartbeat_loop())


@router.post("/color-wave/publish")
async def publish_wave(data: dict):
    source = data.get("source", "manual")
    limits = {
        "heartbeat": (2, 60),  # 2 per minute
        "manual": (10, 60),
    }
    limit, window_sec = limits.get(source, (5, 60))

    allowed, remaining = await check_source_limit(source, limit, window_sec)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "source": source,
                "X-RateLimit-Limit": limit,
                "X-RateLimit-Remaining": remaining,
            },
        )

    client = await _get_redis()
    try:
        data.setdefault("source", source)
        await client.publish(CHANNEL, json.dumps(data))
        return {"ok": True, "source": source, "remaining": remaining}
    finally:
        with contextlib.suppress(Exception):
            await client.close()

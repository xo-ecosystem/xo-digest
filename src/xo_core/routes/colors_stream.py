from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
import asyncio
import json
import os
from redis import asyncio as redis
import contextlib
from xo_core.routes.ops_colors import _check_token as _ops_check_token
import random


router = APIRouter(tags=["colors"])

COLORS_FILE = os.path.join("public", "drops", "colors.json")
COLORS_CHANNEL = os.getenv("XO_COLORS_CHANNEL", "xo:colors:update")

# In-memory subscribers queue set
_subscribers: set[asyncio.Queue] = set()
_listener_task: asyncio.Task | None = None


async def _get_redis() -> redis.Redis:
    return redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True
    )


async def _color_event_generator():
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.add(queue)
    try:
        while True:
            data = await queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    finally:
        _subscribers.discard(queue)


async def _listen_for_colors_updates() -> None:
    client = await _get_redis()
    pubsub = client.pubsub()
    await pubsub.subscribe(COLORS_CHANNEL)
    try:
        async for message in pubsub.listen():
            if message and message.get("type") == "message":
                try:
                    mapping = json.loads(message.get("data") or "{}")
                except Exception:
                    mapping = {}
                for queue in list(_subscribers):
                    try:
                        queue.put_nowait(mapping)
                    except Exception:
                        _subscribers.discard(queue)
    finally:
        with contextlib.suppress(Exception):
            await pubsub.unsubscribe(COLORS_CHANNEL)
            await pubsub.close()
        with contextlib.suppress(Exception):
            await client.close()


async def start_colors_listener():
    global _listener_task
    if _listener_task is None or _listener_task.done():
        _listener_task = asyncio.create_task(_listen_for_colors_updates())


@router.get("/stream/colors")
async def stream_colors():
    return StreamingResponse(_color_event_generator(), media_type="text/event-stream")


async def broadcast_colors_update(mapping: dict) -> None:
    # Push to local subscribers
    for queue in list(_subscribers):
        try:
            queue.put_nowait(mapping)
        except Exception:
            _subscribers.discard(queue)
    # Publish to Redis for other workers
    client = await _get_redis()
    try:
        await client.publish(COLORS_CHANNEL, json.dumps(mapping))
    finally:
        with contextlib.suppress(Exception):
            await client.close()


# Test endpoint to broadcast dummy mapping without modifying colors.json
TEST_MAPPING = {
    "zone-alpha": "#ff00ff",
    "zone-beta": "#00ffff",
    "zone-gamma": "#ffff00",
}


@router.post("/ops/colors/test")
async def test_colors(token: str):
    _ops_check_token(token)
    await broadcast_colors_update(TEST_MAPPING)
    return {
        "ok": True,
        "test_mapping": TEST_MAPPING,
        "note": "This did not modify colors.json",
    }


# Rolling wave simulator for stress testing
ZONES = ["zone-alpha", "zone-beta", "zone-gamma", "zone-delta"]
COLOR_PALETTE = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"]


@router.post("/ops/colors/wave")
async def colors_wave(
    token: str,
    cycles: int = 10,
    delay: float = 1.0,
    background_tasks: BackgroundTasks | None = None,
):
    _ops_check_token(token)

    async def _wave():
        for _ in range(cycles):
            mapping = {zone: random.choice(COLOR_PALETTE) for zone in ZONES}
            await broadcast_colors_update(mapping)
            await asyncio.sleep(delay)

    if background_tasks is not None:
        background_tasks.add_task(_wave)
        return {"ok": True, "mode": "background", "cycles": cycles, "delay": delay}

    await _wave()
    return {"ok": True, "mode": "inline", "cycles": cycles, "delay": delay}

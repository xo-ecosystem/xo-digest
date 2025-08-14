import json
import os
from typing import Optional

from redis.asyncio import Redis


_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis_broadcast: Optional[Redis] = None


def get_redis_broadcast() -> Redis:
    global _redis_broadcast
    if _redis_broadcast is None:
        _redis_broadcast = Redis.from_url(_REDIS_URL)
    return _redis_broadcast


async def publish_to_channel(channel: str, message: dict) -> None:
    """Publish a JSON message to the given Redis pubsub channel."""
    r = get_redis_broadcast()
    await r.publish(channel, json.dumps(message, ensure_ascii=False))


async def broadcast_event(
    channel: str, event_type: str, payload: dict | None = None
) -> None:
    """Publish a standardized event envelope to a channel.

    Envelope: { "type": event_type, ...payload }
    """
    envelope = {"type": event_type}
    if payload:
        envelope.update(payload)
    await publish_to_channel(channel, envelope)

import os
import json
import asyncio
from typing import AsyncGenerator, Set

REDIS_URL = os.getenv("REDIS_URL", "").strip() or None


class InMemoryBus:
    """Simple process-local broadcast bus (good for dev or single worker)."""

    def __init__(self) -> None:
        self._subs: Set[asyncio.Queue] = set()

    async def publish(self, obj: dict) -> None:
        for q in list(self._subs):
            try:
                q.put_nowait(obj)
            except Exception:
                self._subs.discard(q)

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        q: asyncio.Queue = asyncio.Queue()
        self._subs.add(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self._subs.discard(q)

    async def close(self) -> None:
        pass


class RedisBus:
    """Redis pub/sub broadcaster (works across many workers)."""

    def __init__(self, url: str, channel: str = "mb:events") -> None:
        from redis.asyncio import Redis  # optional dependency

        self._redis = Redis.from_url(url)
        self._channel = channel

    async def publish(self, obj: dict) -> None:
        data = json.dumps(obj, ensure_ascii=False)
        await self._redis.publish(self._channel, data)

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)
        try:
            async for message in pubsub.listen():
                if not message or message.get("type") != "message":
                    continue
                data = message.get("data")
                if isinstance(data, (bytes, bytearray)):
                    data = data.decode("utf-8", "ignore")
                try:
                    yield json.loads(data)
                except Exception:
                    continue
        finally:
            try:
                await pubsub.unsubscribe(self._channel)
                await pubsub.close()
            except Exception:
                pass

    async def close(self) -> None:
        try:
            await self._redis.aclose()
        except Exception:
            pass


_bus_singleton = None


def get_bus():
    """Lazy singleton: RedisBus if REDIS_URL is present, else InMemoryBus."""
    global _bus_singleton
    if _bus_singleton is None:
        if REDIS_URL:
            _bus_singleton = RedisBus(REDIS_URL)
        else:
            _bus_singleton = InMemoryBus()
    return _bus_singleton


async def bus_close():
    bus = get_bus()
    close = getattr(bus, "close", None)
    if close:
        await close()

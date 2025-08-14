import os
from typing import Optional, Tuple
from redis.asyncio import Redis


class RedisLimiter:
    """
    Windowed counter limiter using Redis (shared across processes/workers).
    Interface mirrors SimpleLimiter:
      - .default_limit
      - .allow(identifier) -> bool
      - .remaining(identifier) -> int
      - .reset_in_s() -> int
    Keys: {namespace}:{window_ts}:{identifier}
    """

    def __init__(
        self,
        redis: Optional[Redis] = None,
        *,
        limit: int = 60,
        window_s: int = 60,
        namespace: str = "ratelimit",
        redis_url: Optional[str] = None,
    ):
        self.default_limit = int(limit)
        self.window_s = int(window_s)
        self.ns = namespace

        if redis is not None:
            self.r = redis
        else:
            url = redis_url or os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
            self.r = Redis.from_url(url, encoding="utf-8", decode_responses=True)

    async def _redis_time(self) -> int:
        try:
            sec, _ = await self.r.time()
            return int(sec)
        except Exception:
            import time

            return int(time.time())

    async def _window_and_reset(self) -> Tuple[int, int]:
        now = await self._redis_time()
        window_start = now - (now % self.window_s)
        reset_in = (window_start + self.window_s) - now
        return window_start, reset_in

    def _key(self, window_start: int, ident: str) -> str:
        return f"{self.ns}:{window_start}:{ident}"

    async def allow(self, identifier: str) -> bool:
        window_start, _ = await self._window_and_reset()
        key = self._key(window_start, identifier)

        async with self.r.pipeline(transaction=True) as pipe:
            pipe.incr(key, amount=1)
            pipe.ttl(key)
            count, ttl = await pipe.execute()

        count = int(count)
        ttl = int(ttl)

        if ttl == -1:
            _, reset_in = await self._window_and_reset()
            await self.r.expire(key, reset_in)

        return count <= self.default_limit

    async def remaining(self, identifier: str) -> int:
        window_start, _ = await self._window_and_reset()
        key = self._key(window_start, identifier)
        val = await self.r.get(key)
        count = int(val) if val is not None else 0
        return max(0, self.default_limit - count)

    async def reset_in_s(self) -> int:
        _, reset_in = await self._window_and_reset()
        return max(0, int(reset_in))

from __future__ import annotations
import os
import time
from typing import Optional
import json

_REDIS_URL = os.getenv("REDIS_URL", "").strip() or None
_redis_singleton = None


async def _get_redis():
    global _redis_singleton
    if not _REDIS_URL:
        return None
    if _redis_singleton is None:
        from redis.asyncio import Redis  # type: ignore

        _redis_singleton = Redis.from_url(_REDIS_URL)
    return _redis_singleton


class RateLimiter:
    """
    Fixed-window Redis rate limiter.
    Uses key: rl:{bucket}:{identifier}:{window_start}
    When REDIS_URL is not set, allows all requests (no-op limiter).
    """

    def __init__(
        self, bucket: str = "ops", default_limit: int = 30, window_s: int = 60
    ):
        self.bucket = bucket
        self.default_limit = int(default_limit)
        self.window_s = int(window_s)

    def _window_bucket(self) -> int:
        now = int(time.time())
        return now - (now % self.window_s)

    def _key(self, identifier: str) -> str:
        return f"rl:{self.bucket}:{identifier}:{self._window_bucket()}"

    async def allow(
        self,
        identifier: str,
        limit: Optional[int] = None,
        window_s: Optional[int] = None,
    ) -> bool:
        limit = int(limit or self.default_limit)
        window = int(window_s or self.window_s)
        r = await _get_redis()
        if r is None:
            return True
        key = self._key(identifier)
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        count, _ = await pipe.execute()
        try:
            count_val = int(count)
        except Exception:
            count_val = limit  # be safe
        return count_val <= limit

    async def remaining(self, identifier: str, limit: Optional[int] = None) -> int:
        limit = int(limit or self.default_limit)
        r = await _get_redis()
        if r is None:
            return limit
        key = self._key(identifier)
        val = await r.get(key)
        used = int(val) if val else 0
        return max(0, limit - used)


# ---------------- Token-bucket per-channel limiter (Lua) -----------------

_TB_LUA = r"""
local key = KEYS[1]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_rate = tonumber(ARGV[3])
local tokens = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local current_tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])
if not current_tokens then
  current_tokens = capacity
  last_refill = now
else
  local delta = math.max(0, now - last_refill)
  local refill_amount = delta * refill_rate
  current_tokens = math.min(capacity, current_tokens + refill_amount)
  last_refill = now
end

local allowed = 0
if current_tokens >= tokens then
  current_tokens = current_tokens - tokens
  allowed = 1
end

redis.call('HMSET', key, 'tokens', current_tokens, 'last_refill', last_refill)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)

return {allowed, current_tokens}
"""


async def allow_publish(
    channel: str, capacity: int = 5, refill_rate: float = 0.5, tokens: int = 1
) -> tuple[bool, float]:
    """
    Token bucket limiter: capacity tokens max, refill_rate tokens/sec.
    Returns (allowed: bool, remaining: float). If Redis is unavailable, always allows.
    """
    r = await _get_redis()
    if r is None:
        return True, float("inf")
    now = time.time()
    key = f"ratelimit:{channel}"
    try:
        res = await r.eval(
            _TB_LUA, numkeys=1, keys=[key], args=[now, capacity, refill_rate, tokens]
        )
    except TypeError:
        # redis-py older signature
        res = await r.eval(_TB_LUA, 1, key, now, capacity, refill_rate, tokens)
    allowed = bool(res[0])
    remaining = float(res[1])
    return allowed, remaining


async def allow_publish_per_ip(
    drop_id: str,
    client_ip: str,
    tokens: int = 1,
) -> tuple[bool, float, int, float]:
    """
    Per-IP + per-drop token bucket to isolate abuse.
    Returns (allowed, remaining, capacity, refill_rate). Allows if Redis unavailable.
    """
    capacity, refill_rate = await get_or_init_drop_limit_config(drop_id)
    r = await _get_redis()
    if r is None:
        return True, float("inf"), capacity, refill_rate
    now = time.time()
    key = f"ratelimit:{drop_id}:{client_ip}"
    try:
        res = await r.eval(
            _TB_LUA, numkeys=1, keys=[key], args=[now, capacity, refill_rate, tokens]
        )
    except TypeError:
        res = await r.eval(_TB_LUA, 1, key, now, capacity, refill_rate, tokens)
    allowed = bool(res[0])
    remaining = float(res[1])
    return allowed, remaining, capacity, refill_rate


# ---------------- Per-drop config (Redis) -----------------

DEFAULT_CAPACITY = 5
DEFAULT_REFILL = 0.5


async def get_drop_limit_config(drop_id: str) -> tuple[int, float]:
    """
    Returns (capacity, refill_rate) from Redis config, or defaults.
    Redis key: ratelimit_config:<drop_id>
    Value: JSON {"capacity": int, "refill_rate": float}
    """
    r = await _get_redis()
    if r is None:
        return DEFAULT_CAPACITY, DEFAULT_REFILL
    raw = await r.get(f"ratelimit_config:{drop_id}")
    if not raw:
        return DEFAULT_CAPACITY, DEFAULT_REFILL
    try:
        cfg = json.loads(raw)
        return int(cfg.get("capacity", DEFAULT_CAPACITY)), float(
            cfg.get("refill_rate", DEFAULT_REFILL)
        )
    except Exception:
        return DEFAULT_CAPACITY, DEFAULT_REFILL


async def set_drop_limit_config(
    drop_id: str, capacity: int, refill_rate: float
) -> None:
    r = await _get_redis()
    if r is None:
        return
    cfg = json.dumps({"capacity": int(capacity), "refill_rate": float(refill_rate)})
    await r.set(f"ratelimit_config:{drop_id}", cfg)


async def get_or_init_drop_limit_config(drop_id: str) -> tuple[int, float]:
    """
    Returns (capacity, refill_rate) and initializes defaults if missing.
    """
    r = await _get_redis()
    if r is None:
        return DEFAULT_CAPACITY, DEFAULT_REFILL
    key = f"ratelimit_config:{drop_id}"
    raw = await r.get(key)
    if not raw:
        cfg = json.dumps({"capacity": DEFAULT_CAPACITY, "refill_rate": DEFAULT_REFILL})
        await r.set(key, cfg)
        # Broadcast system event announcing new channel
        try:
            from xo_core.services.broadcast import broadcast_event

            await broadcast_event(
                channel=f"drop:{drop_id}",
                event_type="system",
                payload={
                    "message": f"📡 New channel `{drop_id}` opened",
                    "capacity": DEFAULT_CAPACITY,
                    "refill_rate": DEFAULT_REFILL,
                    "timestamp": time.time(),
                },
            )
        except Exception:
            pass
        return DEFAULT_CAPACITY, DEFAULT_REFILL
    try:
        cfg = json.loads(raw)
        return int(cfg.get("capacity", DEFAULT_CAPACITY)), float(
            cfg.get("refill_rate", DEFAULT_REFILL)
        )
    except Exception:
        return DEFAULT_CAPACITY, DEFAULT_REFILL

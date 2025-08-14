import os
from typing import Optional, Tuple

from redis.asyncio import Redis


# Lua script — atomic token bucket:
# KEY[1] = hash key for bucket
# ARGV:
#   1 = capacity (int)
#   2 = refill_per_sec (float as string)
#   3 = req_tokens (int)
#   4 = ttl_seconds (int)   (how long to keep idle buckets)
# Returns: { allowed(0/1), remaining_tokens(int), wait_seconds(int) }
LUA_TOKEN_BUCKET = r"""
local k = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_per_sec = tonumber(ARGV[2])
local req = tonumber(ARGV[3])
local ttl = tonumber(ARGV[4])

-- current time
local t = redis.call('TIME')  -- {sec, usec}
local now = tonumber(t[1]) + tonumber(t[2]) / 1000000.0

-- load state
local h = redis.call('HMGET', k, 'tokens', 'ts')
local tokens = tonumber(h[1])
local ts = tonumber(h[2])

if not tokens then
  tokens = capacity
  ts = now
else
  -- refill
  local delta = math.max(0.0, now - ts)
  local filled = tokens + delta * refill_per_sec
  if filled > capacity then filled = capacity end
  tokens = filled
  ts = now
end

local allowed = 0
local wait_s = 0
if tokens >= req then
  tokens = tokens - req
  allowed = 1
else
  -- how long until we have enough tokens?
  wait_s = math.ceil((req - tokens) / refill_per_sec)
end

-- persist state
redis.call('HMSET', k, 'tokens', tokens, 'ts', ts)
-- idle eviction (optional; keep a couple of bucket-half-lives)
redis.call('EXPIRE', k, ttl)

-- remaining visible as int
local remaining = math.floor(tokens + 0.000001)
return { allowed, remaining, wait_s }
"""


class RedisTokenBucketLimiter:
    """
    Token-bucket limiter using Redis + Lua (1 RTT per decision).
    Good for bursty traffic; supports variable cost via allow(identifier, tokens=1).

    Args:
      capacity: max tokens bucket can hold (burst size)
      refill_per_sec: tokens added per second (sustained rate)
      idle_ttl_s: expire idle buckets
      namespace: key prefix
      redis_url | redis: connection
    """

    def __init__(
        self,
        redis: Optional[Redis] = None,
        *,
        capacity: int = 60,
        refill_per_sec: float = 1.0,
        idle_ttl_s: Optional[int] = None,
        namespace: str = "ratelimit:tb",
        redis_url: Optional[str] = None,
    ):
        self.capacity = int(capacity)
        self.refill = float(refill_per_sec)
        if idle_ttl_s is None:
            idle_ttl_s = max(30, int(2 * (self.capacity / max(self.refill, 0.0001))))
        self.idle_ttl_s = int(idle_ttl_s)
        self.ns = namespace

        if redis is not None:
            self.r = redis
        else:
            url = redis_url or os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
            self.r = Redis.from_url(url, encoding="utf-8", decode_responses=True)

        self._sha: Optional[str] = None

        # For middleware header reporting
        self.default_limit = self.capacity  # report as burst capacity
        self.window_s = 1  # not used; kept for compatibility

    def _key(self, ident: str) -> str:
        return f"{self.ns}:{ident}"

    async def _ensure_script(self):
        if not self._sha:
            self._sha = await self.r.script_load(LUA_TOKEN_BUCKET)

    # Public API (compatible superset):
    async def allow(self, identifier: str, tokens: int = 1) -> bool:
        await self._ensure_script()
        k = self._key(identifier)
        try:
            res = await self.r.evalsha(
                self._sha,
                1,
                k,
                str(self.capacity),
                repr(self.refill),
                str(int(tokens)),
                str(self.idle_ttl_s),
            )
        except Exception:
            self._sha = await self.r.script_load(LUA_TOKEN_BUCKET)
            res = await self.r.evalsha(
                self._sha,
                1,
                k,
                str(self.capacity),
                repr(self.refill),
                str(int(tokens)),
                str(self.idle_ttl_s),
            )
        return int(res[0]) == 1

    async def remaining(self, identifier: str) -> int:
        await self._ensure_script()
        k = self._key(identifier)
        res = await self.r.evalsha(
            self._sha,
            1,
            k,
            str(self.capacity),
            repr(self.refill),
            "0",
            str(self.idle_ttl_s),
        )
        return int(res[1])

    async def reset_in_s(self, identifier: Optional[str] = None) -> int:
        if not identifier:
            return 1
        await self._ensure_script()
        k = self._key(identifier)
        res = await self.r.evalsha(
            self._sha,
            1,
            k,
            str(self.capacity),
            repr(self.refill),
            "1",
            str(self.idle_ttl_s),
        )
        return int(res[2])

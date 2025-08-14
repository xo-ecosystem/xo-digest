import os
from typing import Tuple

from redis import asyncio as redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


# Lua script implements a simple fixed-window counter per source
# Returns array: [allowed_flag, remaining]
RATE_LIMIT_LUA = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local current = tonumber(redis.call('GET', key) or '0')

if current >= limit then
  return {0, limit - current}
else
  if current == 0 then
    redis.call('SET', key, 1, 'EX', ttl)
  else
    redis.call('INCR', key)
  end
  return {1, limit - (current + 1)}
end
"""


async def _get_client() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


async def check_source_limit(
    source: str, limit: int, window_sec: int
) -> Tuple[bool, int]:
    client = await _get_client()
    try:
        key = f"ratelimit:colorwave:{source}"
        # Load script and eval
        sha = await client.script_load(RATE_LIMIT_LUA)
        allowed, remaining = await client.evalsha(sha, 1, key, limit, window_sec)
        # Normalize outputs
        try:
            allowed_flag = bool(int(allowed))
        except Exception:
            allowed_flag = bool(allowed)
        try:
            remaining_int = int(remaining)
        except Exception:
            remaining_int = 0
        if remaining_int < 0:
            remaining_int = 0
        return allowed_flag, remaining_int
    finally:
        await client.close()

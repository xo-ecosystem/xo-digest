import time
from typing import Dict, Tuple


class SimpleLimiter:
    """
    Token-bucket-ish per-identifier limiter.
    Windowed counter: limit N requests per window_s per identifier.
    """

    def __init__(self, limit: int = 60, window_s: int = 60):
        self.default_limit = int(limit)
        self.window_s = int(window_s)
        self._buckets: Dict[str, Tuple[int, int]] = {}

    def _now(self) -> int:
        return int(time.time())

    def _window(self, now_ts: int) -> int:
        return now_ts - (now_ts % self.window_s)

    def _reset_in_s(self, now_ts: int) -> int:
        return (self._window(now_ts) + self.window_s) - now_ts

    def allow(self, identifier: str) -> bool:
        now = self._now()
        w = self._window(now)
        start, count = self._buckets.get(identifier, (w, 0))
        if start != w:
            start, count = w, 0
        if count < self.default_limit:
            self._buckets[identifier] = (start, count + 1)
            return True
        self._buckets[identifier] = (start, count)
        return False

    def remaining(self, identifier: str) -> int:
        now = self._now()
        w = self._window(now)
        start, count = self._buckets.get(identifier, (w, 0))
        if start != w:
            return self.default_limit
        return max(0, self.default_limit - count)

    def reset_in_s(self) -> int:
        return self._reset_in_s(self._now())

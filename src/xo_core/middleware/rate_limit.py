from typing import Callable, Optional, Iterable
import inspect
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from xo_core.utils.rate_limit import SimpleLimiter


def default_identifier(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return req.client.host if req.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    - Adds X-RateLimit-Limit / Remaining / Reset on 200s
    - On limit exceeded, returns 429 with Retry-After
    - Can scope to specific paths with `only_paths` (prefix match)
    """

    def __init__(
        self,
        app,
        limiter: SimpleLimiter,
        only_paths: Optional[Iterable[str]] = None,
        identify: Callable[[Request], str] = default_identifier,
        enforce: bool = True,
    ):
        super().__init__(app)
        self.limiter = limiter
        self.only_paths = list(only_paths) if only_paths else None
        self.identify = identify
        self.enforce = enforce

    def _applies(self, path: str) -> bool:
        if not self.only_paths:
            return True
        return any(path.startswith(p) for p in self.only_paths)

    async def dispatch(self, request: Request, call_next):
        applies = self._applies(request.url.path)
        ident = self.identify(request)

        async def _call(method, *args, **kwargs):
            val = method(*args, **kwargs)
            if inspect.isawaitable(val):
                return await val
            return val

        limit = self.limiter.default_limit
        remaining = await _call(self.limiter.remaining, ident)
        reset_in = await _call(self.limiter.reset_in_s)

        if applies:
            allowed = await _call(self.limiter.allow, ident)
            if not allowed and self.enforce:
                headers = {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_in),
                    "Retry-After": str(reset_in),
                }
                return JSONResponse(
                    {"error": "rate_limited", "retry_in_s": reset_in},
                    status_code=429,
                    headers=headers,
                )

        response: Response = await call_next(request)

        if applies:
            remaining = await _call(self.limiter.remaining, ident)
            reset_in = await _call(self.limiter.reset_in_s)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_in)

        return response

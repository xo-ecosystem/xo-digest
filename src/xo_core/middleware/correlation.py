import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from xo_core.logging import set_request_context, new_request_id, get_logger


log = get_logger("xo.correlation")


class CorrelationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable):
        req_id = request.headers.get(self.header_name) or new_request_id()
        route = request.url.path
        method = request.method
        set_request_context(req_id, route, method)

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000.0
            log.exception(
                "unhandled_exception",
                extra={
                    "path": route,
                    "duration_ms": round(duration_ms, 2),
                    "client": request.client.host if request.client else None,
                },
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000.0
        response.headers[self.header_name] = req_id

        log.info(
            "request_complete",
            extra={
                "path": route,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "client": request.client.host if request.client else None,
            },
        )
        return response

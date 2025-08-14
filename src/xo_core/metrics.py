import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from prometheus_client import (
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
)

# Use the default global REGISTRY so /metrics can export everything at once.
registry: CollectorRegistry = REGISTRY

# Process start time (epoch seconds)
PROCESS_START_TIME = time.time()

# Core app metrics
APP_INFO = Gauge(
    "app_info",
    "Basic app info",
    labelnames=("app", "version"),
    registry=registry,
)
APP_UPTIME_SECONDS = Gauge(
    "app_uptime_seconds",
    "Seconds since app start",
    registry=registry,
)

# HTTP metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=("method", "path", "status"),
    registry=registry,
)

HTTP_REQUEST_INFLIGHT = Gauge(
    "http_requests_inflight",
    "In-flight HTTP requests",
    registry=registry,
)

HTTP_REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_latency_seconds",
    "Request latency in seconds",
    labelnames=("method", "path", "status"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
    registry=registry,
)

## ==== Business metrics (Message Bottle) ====
MESSAGE_BOTTLE_PUBLISHES_TOTAL = Counter(
    "message_bottle_publishes_total",
    "Total Message Bottle publish requests accepted",
    labelnames=("source",),  # e.g., "api", "cron", "admin"
    registry=registry,
)
MESSAGE_BOTTLE_PAYLOAD_BYTES_TOTAL = Counter(
    "message_bottle_payload_bytes_total",
    "Total payload bytes received for Message Bottle publishes",
    registry=registry,
)

## ==== Business metrics (Digest) ====
DIGEST_PUBLISHES_TOTAL = Counter(
    "digest_publishes_total",
    "Total Digest publish requests accepted",
    labelnames=("format",),  # e.g., "html", "md", "txt"
    registry=registry,
)
DIGEST_CONTENT_BYTES_TOTAL = Counter(
    "digest_content_bytes_total",
    "Total content bytes published into digest",
    registry=registry,
)

# Optional: current queued items (if you later add queues/workers)
PUBLISH_QUEUE_DEPTH = Gauge(
    "publish_queue_depth",
    "How many items are queued for background publish",
    labelnames=("queue",),  # e.g., "message_bottle", "digest"
    registry=registry,
)


def _canonical_path(request: Request) -> str:
    """
    Best-effort path templating. Falls back to raw path if route is unavailable.
    """
    route = getattr(request, "scope", {}).get("route")
    if route and getattr(route, "path_format", None):
        return route.path_format
    if route and getattr(route, "path", None):
        return route.path
    return request.url.path  # fallback


class PrometheusTimingMiddleware(BaseHTTPMiddleware):
    """
    Times every request and records:
      - in-flight gauge
      - total counter (by method, templated path, status)
      - latency histogram (by method, templated path, status)
    Also updates uptime gauge each request (cheap).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        HTTP_REQUEST_INFLIGHT.inc()
        start = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            method = request.method
            path = _canonical_path(request)
            status = "500"
            try:
                if response is not None:
                    status = str(response.status_code)
            except Exception:
                pass

            HTTP_REQUESTS_TOTAL.labels(method=method, path=path, status=status).inc()
            HTTP_REQUEST_LATENCY_SECONDS.labels(
                method=method, path=path, status=status
            ).observe(duration)
            HTTP_REQUEST_INFLIGHT.dec()

            # Update uptime
            APP_UPTIME_SECONDS.set(time.time() - PROCESS_START_TIME)


def init_metrics(app_name: str, version: str = "0.1.0") -> None:
    """
    Initialize gauges that should be set once at startup.
    """
    APP_INFO.labels(app=app_name, version=version).set(1)
    APP_UPTIME_SECONDS.set(0.0)

import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from xo_agents.api import app as webhook_router
from xo_core.routes.inbox import router as inbox_router
from xo_core.routes.socials import router as socials_router
from xo_core.routes.message_bottle import router as message_bottle_router
from xo_core.routes.digest import router as digest_router
from xo_core.routes.health import router as health_router
from xo_core.routes.ops import router as ops_router
from xo_core.routes.stream import router as stream_router
from xo_core.routes.colors_stream import router as colors_stream_router, start_colors_listener
from xo_core.routes.color_wave import (
    router as color_wave_router,
    start_color_wave_heartbeat,
)
from xo_core.routes.ops_colors import router as ops_colors_router
from xo_core.metrics import PrometheusTimingMiddleware, init_metrics
from xo_core.logging import setup_logging, get_logger
from xo_core.middleware.correlation import CorrelationMiddleware
from xo_core.telemetry import setup_otel
from xo_core.access_log import AccessLogMiddleware
from xo_core.rate_limit import install_rate_limiting
from xo_core.utils.rate_limit import SimpleLimiter
from xo_core.middleware.rate_limit import RateLimitMiddleware

log = logging.getLogger(__name__)

setup_logging()
log = get_logger("xo.app")

app = FastAPI()
setup_otel(app)

# Optional CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in (os.getenv("CORS_ALLOW_ORIGINS", "*"),) if origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus timing middleware
app.add_middleware(PrometheusTimingMiddleware)
app.add_middleware(CorrelationMiddleware)
app.add_middleware(AccessLogMiddleware)
install_rate_limiting(app)
LIMIT = int(os.getenv("XO_RATE_LIMIT", "60"))
WINDOW = int(os.getenv("XO_RATE_WINDOW_S", "60"))
MODE = os.getenv("XO_RATE_LIMIT_MODE", "simple").lower()
if MODE == "simple":
_global_limiter = SimpleLimiter(limit=LIMIT, window_s=WINDOW)
elif MODE == "redis_lua":
    from xo_core.utils.rate_limit_redis_lua import RedisLuaLimiter

    _global_limiter = RedisLuaLimiter(
        limit=LIMIT, window_s=WINDOW, namespace="xo:ratelimit"
    )
elif MODE == "redis":
    from xo_core.utils.rate_limit_redis import RedisLimiter

    _global_limiter = RedisLimiter(
        limit=LIMIT, window_s=WINDOW, namespace="xo:ratelimit"
    )
elif MODE == "tokenbucket":
    from xo_core.utils.rate_limit_redis_tokenbucket import RedisTokenBucketLimiter

    _global_limiter = RedisTokenBucketLimiter(
        capacity=int(os.getenv("XO_TB_CAPACITY", "20")),
        refill_per_sec=float(os.getenv("XO_TB_REFILL_PER_SEC", "2")),
        idle_ttl_s=int(os.getenv("XO_TB_IDLE_TTL", "120")),
        namespace="xo:ratelimit:tb",
    )
else:
    raise RuntimeError(f"Unknown XO_RATE_LIMIT_MODE={MODE}")
SCOPED_PATHS = [
    "/message-bottle/publish",
    "/ops/broadcast",
    "/message-bottle/stream",
]
app.add_middleware(
    RateLimitMiddleware,
    limiter=_global_limiter,
    only_paths=SCOPED_PATHS,
    enforce=True,
)

# Expose limiter for diagnostics/tuning endpoints
app.state.limiter = _global_limiter

# Routers
app.mount("/agent", webhook_router)
app.include_router(inbox_router)
app.include_router(socials_router)
app.include_router(message_bottle_router)
app.include_router(digest_router)
from xo_core.routes.debug_echo import router as debug_echo_router

app.include_router(health_router)
app.include_router(debug_echo_router)
app.include_router(ops_router)
app.include_router(stream_router)
app.include_router(ops_colors_router)
app.include_router(colors_stream_router)
app.include_router(color_wave_router)

try:
    # Mount GitHub webhook router
    from xo_core.webhooks.github import router as github_webhook_router
except Exception:
    github_webhook_router = None

# Include router if available (keeps dev flexible)
if github_webhook_router:
    app.include_router(github_webhook_router, prefix="")


@app.get("/")
def read_root():
    return {"app": "xo-core", "status": "ok"}


@app.on_event("startup")
async def _startup_metrics():
    init_metrics(app_name="xo-core", version="0.1.0")
    # ensure colors stream Redis listener is running
    await start_colors_listener()
    # optionally start color wave heartbeat publisher
    await start_color_wave_heartbeat()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.warning(
        "validation_error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "extra": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content={"ok": False, "error": "validation_error", "details": exc.errors()},
    )


@app.middleware("http")
async def error_wrapper(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        log.exception(
            "internal_error", extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=500, content={"ok": False, "error": "internal_server_error"}
        )

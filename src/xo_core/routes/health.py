import os
from datetime import datetime

from fastapi import APIRouter, Response, Query
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from xo_core.services.message_bottle import publish_message as _mb_publish
from xo_core.services.digest import publish_digest as _dg_publish
from xo_core.logging import get_logger
from opentelemetry import trace


router = APIRouter(tags=["system"])
log = get_logger("xo.debug")


@router.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/metrics")
def metrics():
    output = generate_latest(REGISTRY)
    return Response(content=output, media_type=CONTENT_TYPE_LATEST)


@router.post("/debug/metrics-test")
def metrics_test(samples: int = 3):
    """
    Exercises business and HTTP metrics without side effects.
    Calls the stubbed services a few times with tiny payloads.
    """
    samples = max(1, min(int(samples), 50))
    for i in range(samples):
        _mb_publish({"hello": "world", "i": i}, source="debug")
        _dg_publish(title=f"sample-{i}", content="# hi\nok", fmt="md")
    return {"ok": True, "samples": samples}


@router.post("/debug/logs-test")
def logs_test(
    level: str = Query("info", pattern="^(debug|info|warning|error|critical)$")
):
    msg = {"event": "logs_test", "note": "emitting sample lines"}
    lvl = level.lower()
    if lvl == "debug":
        log.debug("debug sample", extra={"extra": msg})
    if lvl == "info":
        log.info("info sample", extra={"extra": msg})
    if lvl == "warning":
        log.warning("warning sample", extra={"extra": msg})
    if lvl == "error":
        log.error("error sample", extra={"extra": msg})
    if lvl == "critical":
        log.critical("critical sample", extra={"extra": msg})
    return {"ok": True, "level": lvl}


@router.get("/debug/trace-test")
def trace_test():
    tracer = trace.get_tracer("xo.debug")
    with tracer.start_as_current_span("trace_test_span"):
        log.info("trace_test event", extra={"extra": {"hello": "world"}})
    return {"ok": True, "traced": True}


@router.get("/health")
async def health_root():
    return {"ok": True}


@router.get("/health/redis")
async def health_redis():
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        return {
            "ok": True,
            "redis": {"enabled": False, "status": "disabled (using in-memory bus)"},
        }
    try:
        from redis.asyncio import Redis  # type: ignore

        r = Redis.from_url(url)
        pong = await r.ping()
        await r.aclose()
        return {
            "ok": bool(pong),
            "redis": {"enabled": True, "status": "pong" if pong else "no-pong"},
        }
    except Exception as e:
        return {
            "ok": False,
            "redis": {"enabled": True, "status": f"error: {type(e).__name__}: {e}"},
        }

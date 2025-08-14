import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Header, Query, Request
from fastapi.responses import JSONResponse, Response
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_429_TOO_MANY_REQUESTS
from pydantic import BaseModel

from xo_core.services.bus import get_bus
from xo_core.services.rate_limit import RateLimiter
import time


router = APIRouter(tags=["ops"])

# Read once at import (keeps request path hot)
OPS_TOKEN = os.getenv("OPS_BROADCAST_TOKEN", "").strip()


class BroadcastIn(BaseModel):
    type: str = "message_bottle.new"
    payload: Dict[str, Any]


def _build_default_payload(name: str, message: str) -> Dict[str, Any]:
    return {
        "name": name,
        "message": message,
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "ops",
    }


def _auth_or_403(token_header: Optional[str]):
    if not OPS_TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="OPS token not configured"
        )
    token = None
    if token_header and token_header.lower().startswith("bearer "):
        token = token_header[7:].strip()
    return token


@router.get("/ops/ping")
async def ops_ping(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_ops_token: Optional[str] = Header(None, convert_underscores=False),
):
    token = _auth_or_403(authorization)
    token = token or (x_ops_token or "").strip()
    if token != OPS_TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="invalid ops token"
        )
    ip = request.headers.get("x-forwarded-for")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    return {"ok": True, "ip": ip}


_ops_limiter = RateLimiter(bucket="ops-broadcast", default_limit=60, window_s=60)


@router.post("/ops/broadcast")
async def ops_broadcast(
    body: BroadcastIn,
    authorization: Optional[str] = Header(None),
    x_ops_token: Optional[str] = Header(None, convert_underscores=False),
    request: Request = None,
):
    token = _auth_or_403(authorization)
    token = token or (x_ops_token or "").strip()
    if token != OPS_TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid OPS token"
        )

    ip = request.headers.get("x-forwarded-for") if request else None
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.client.host if request and request.client else "unknown"
    allowed = await _ops_limiter.allow(identifier=ip)
    remaining = await _ops_limiter.remaining(ip)
    window_s = _ops_limiter.window_s
    now_ts = int(time.time())
    reset_ts = (now_ts - (now_ts % window_s)) + window_s
    reset_in_s = reset_ts - now_ts

    headers = {
        "X-RateLimit-Limit": str(_ops_limiter.default_limit),
        "X-RateLimit-Remaining": str(remaining if allowed else 0),
        "X-RateLimit-Reset": str(reset_in_s),
    }

    if not allowed:
        headers["Retry-After"] = str(reset_in_s)
        return JSONResponse(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "rate_limited",
                "retry_in_s": reset_in_s,
                "remaining": 0,
            },
            headers=headers,
        )

    bus = get_bus()
    await bus.publish({"type": body.type, "payload": body.payload})
    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "published": body.type,
            "rate": {
                "window_s": window_s,
                "limit": _ops_limiter.default_limit,
                "remaining": remaining,
            },
        },
        headers=headers,
    )


@router.get("/ops/broadcast")
async def ops_broadcast_get(
    name: str = Query("OPS"),
    message: str = Query(..., description="Message text"),
    authorization: Optional[str] = Header(None),
    x_ops_token: Optional[str] = Header(None, convert_underscores=False),
):
    token = _auth_or_403(authorization)
    token = token or (x_ops_token or "").strip()
    if token != OPS_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid OPS token")

    bus = get_bus()
    await bus.publish(
        {
            "type": "message_bottle.new",
            "payload": _build_default_payload(name=name, message=message),
        }
    )
    return {"ok": True, "published": "message_bottle.new"}


class RLTestIn(BaseModel):
    identifier: Optional[str] = None
    tokens: Optional[int] = 1


def _client_ip(req: Request) -> str:
    xfwd = req.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return xfwd or (req.client.host if req.client else "anon")


async def _remaining(limiter, ident: str) -> Optional[int]:
    try:
        return await limiter.remaining(ident)
    except Exception:
        return None


async def _reset_in(limiter, ident: str) -> Optional[int]:
    try:
        return await limiter.reset_in_s(ident)  # token-bucket uses ident
    except TypeError:
        try:
            return await limiter.reset_in_s()  # fixed window signature
        except Exception:
            return None
    except Exception:
        return None


@router.post("/ops/ratelimit/test")
async def ratelimit_test(
    req: Request,
    payload: RLTestIn,
    response: Response,
    x_ops_token: Optional[str] = Header(default=None, alias="X-Ops-Token"),
):
    required = os.getenv("XO_OPS_TOKEN") or OPS_TOKEN
    if not required or x_ops_token != required:
        raise HTTPException(status_code=401, detail="Unauthorized")

    limiter = getattr(req.app.state, "limiter", None)
    if limiter is None:
        raise HTTPException(status_code=500, detail="Limiter not configured")

    ident = payload.identifier or _client_ip(req)
    tokens = int(payload.tokens or 1)

    before = await _remaining(limiter, ident)

    allowed = False
    try:
        allowed = await limiter.allow(
            ident, tokens=tokens
        )  # token-bucket allows tokens
    except TypeError:
        allowed = await limiter.allow(ident)

    after = await _remaining(limiter, ident)

    limit_hdr = getattr(limiter, "default_limit", None)
    if isinstance(limit_hdr, (int, float)) and limit_hdr > 0:
        response.headers["X-RateLimit-Limit"] = str(int(limit_hdr))
    if after is not None:
        response.headers["X-RateLimit-Remaining"] = str(max(0, int(after)))

    if not allowed:
        wait = await _reset_in(limiter, ident)
        if isinstance(wait, (int, float)) and wait and wait > 0:
            response.headers["Retry-After"] = str(int(wait))
        raise HTTPException(
            status_code=429,
            detail={
                "ok": False,
                "reason": "rate_limited",
                "identifier": ident,
                "tokens_requested": tokens,
                "remaining_before": before,
                "remaining_after": after,
                "retry_after_s": int(wait) if isinstance(wait, (int, float)) else None,
            },
        )

    return {
        "ok": True,
        "identifier": ident,
        "tokens_requested": tokens,
        "remaining_before": before,
        "remaining_after": after,
        "mode": getattr(limiter, "__class__", type(limiter)).__name__,
    }


class RLSuggestIn(BaseModel):
    target_qps: float
    burst_factor: Optional[float] = 1.0
    test_seconds: Optional[int] = 5
    identifier: Optional[str] = "test:anon"


@router.post("/ops/ratelimit/suggest")
async def ratelimit_suggest(payload: RLSuggestIn):
    target_qps = max(float(payload.target_qps), 0.1)
    burst_factor = max(float(payload.burst_factor or 1.0), 1.0)
    test_seconds = max(int(payload.test_seconds or 5), 1)
    ident = payload.identifier or "test:anon"

    refill_per_sec = target_qps
    capacity = int(round(target_qps * burst_factor))

    env_lines = [
        f"export XO_TB_CAPACITY={capacity}",
        f"export XO_TB_REFILL_PER_SEC={refill_per_sec:.3f}",
        "export XO_RATE_LIMIT_MODE=tokenbucket",
        "export REDIS_URL=redis://127.0.0.1:6379/0",
    ]

    total_reqs = int(target_qps * test_seconds * 1.5)
    sleep_s = 1.0 / target_qps
    curl_cmd = (
        f"for i in $(seq 1 {total_reqs}); do "
        f"curl -sS -X POST http://localhost:8000/ops/ratelimit/test "
        f"-H \"Content-Type: application/json\" -H \"X-Ops-Token: $XO_OPS_TOKEN\" "
        f"-d '{{\"identifier\":\"{ident}\",\"tokens\":1}}' -i | "
        f"grep -E 'HTTP/|X-Rate|Retry-After|{{\\"|}}$'; "
        f"sleep {sleep_s:.3f}; "
        f"done"
    )

    return {
        "ok": True,
        "input": {
            "target_qps": target_qps,
            "burst_factor": burst_factor,
            "test_seconds": test_seconds,
            "identifier": ident,
        },
        "suggestion": {"capacity": capacity, "refill_per_sec": refill_per_sec},
        "env_setup": env_lines,
        "curl_test": curl_cmd,
        "note": "Set XO_TB_CAPACITY/XO_TB_REFILL_PER_SEC, restart app, run curl_test loop.",
    }

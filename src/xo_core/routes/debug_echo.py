import json
import os
from typing import Any, Dict

from fastapi import APIRouter, Request, Depends
from slowapi.util import get_remote_address
from slowapi import Limiter
from xo_core.rate_limit import get_tier_for_request, get_limit_for_tier

from ..logging import get_logger


router = APIRouter(tags=["debug"])
log = get_logger("debug.echo")


@router.api_route(
    "/debug/echo", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)  # any
async def debug_echo(request: Request) -> Dict[str, Any]:
    max_bytes = int(os.getenv("DEBUG_ECHO_MAX_BODY", "4096"))
    body = await request.body()
    preview = body[:max_bytes]

    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        try:
            parsed = json.loads(preview.decode("utf-8", errors="ignore"))
        except Exception:
            parsed = preview.decode("utf-8", errors="ignore")
    else:
        parsed = preview.decode("utf-8", errors="ignore")

    out = {
        "method": request.method,
        "path": str(request.url.path),
        "query": dict(request.query_params),
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
        "body_preview": parsed,
        "truncated": len(body) > max_bytes,
    }
    log.info("debug_echo", extra={"extra": {"size": len(body), "ctype": ctype}})
    return out


def _get_limiter(request: Request) -> Limiter:
    return request.app.state.limiter


@router.get("/debug/rate-test")
def debug_rate_test(
    request: Request, limiter: Limiter = Depends(_get_limiter)
) -> Dict[str, Any]:
    limit = get_limit_for_tier(get_tier_for_request(request))
    key = request.headers.get("x-api-key") or get_remote_address(request)
    limiter.hit(limit, request=request, key_func=lambda _: key)
    return {
        "ok": True,
        "limit": limit,
        "who": key,
        "hint": "Send requests above your tier limit to see 429 rate limiting.",
    }


@router.get("/debug/whoami")
def debug_whoami(
    request: Request, limiter: Limiter = Depends(_get_limiter)
) -> Dict[str, Any]:
    tier = get_tier_for_request(request)
    limit_str = get_limit_for_tier(tier)
    return {
        "ok": True,
        "tier": tier,
        "limit": limit_str,
        "api_key": request.headers.get("x-api-key") or None,
        "hint": "Change your x-api-key header to switch tiers.",
    }

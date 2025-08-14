import json
import os
import sys
import time
import logging
from typing import Dict, Any, List, Optional
from logging.handlers import TimedRotatingFileHandler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from .logging import new_request_id, set_request_context, get_logger


ACCESS_LOG = logging.getLogger("access")
_WIRED = False

_DEFAULT_REDACT_HEADERS = {"authorization", "cookie", "x-api-key", "x-auth-token"}
_DEFAULT_REDACT_KEYS = {
    "password",
    "token",
    "secret",
    "apikey",
    "api_key",
    "refresh_token",
}


def _build_access_handler() -> list[logging.Handler]:
    fmt = logging.Formatter("%(message)s")
    handlers: list[logging.Handler] = []

    # stdout on by default (can disable with ACCESS_LOG_STDOUT=0)
    if os.getenv("ACCESS_LOG_STDOUT", "1") not in ("0", "false", "False"):
        h = logging.StreamHandler(stream=sys.stdout)
        h.setFormatter(fmt)
        handlers.append(h)

    # file rotate (enable via ACCESS_LOG_FILE)
    log_file = os.getenv("ACCESS_LOG_FILE")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        when = os.getenv("ACCESS_LOG_ROTATE_WHEN", "midnight")
        backup = int(os.getenv("ACCESS_LOG_ROTATE_BACKUP", "14"))
        fh = TimedRotatingFileHandler(
            log_file, when=when, backupCount=backup, encoding="utf-8", utc=True
        )
        fh.setFormatter(fmt)
        handlers.append(fh)

    return handlers


def _wire_logger_once() -> None:
    global _WIRED
    if _WIRED:
        return
    for h in list(ACCESS_LOG.handlers):
        ACCESS_LOG.removeHandler(h)
    for h in _build_access_handler():
        ACCESS_LOG.addHandler(h)
    ACCESS_LOG.setLevel(os.getenv("ACCESS_LOG_LEVEL", "INFO").upper())
    _WIRED = True


def _redact_headers(
    headers: Dict[str, Any], extra_redact: Optional[List[str]] = None
) -> Dict[str, Any]:
    red = set(_DEFAULT_REDACT_HEADERS)
    if extra_redact:
        red |= {h.strip().lower() for h in extra_redact}
    out: Dict[str, Any] = {}
    for k, v in headers.items():
        if k.lower() in red:
            out[k] = "***"
        else:
            out[k] = v
    return out


def _redact_json(obj: Any, extra_redact: Optional[List[str]] = None) -> Any:
    red = set(_DEFAULT_REDACT_KEYS)
    if extra_redact:
        red |= {k.strip().lower() for k in extra_redact}
    if isinstance(obj, dict):
        return {
            k: ("***" if k.lower() in red else _redact_json(v, extra_redact))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact_json(v, extra_redact) for v in obj]
    return obj


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _wire_logger_once()

        # Request context
        rid = request.headers.get("x-request-id") or new_request_id()
        route_path = request.url.path
        method = request.method
        set_request_context(rid, route_path, method)

        # Headers snapshot (redacted)
        redact_hdrs = [
            h
            for h in os.getenv("ACCESS_LOG_REDACT_HEADERS", "").split(",")
            if h.strip()
        ]
        req_headers = _redact_headers(dict(request.headers), redact_hdrs)

        # Optional body capture
        capture_body = os.getenv("ACCESS_LOG_CAPTURE_BODY", "0") in (
            "1",
            "true",
            "True",
        )
        max_bytes = int(os.getenv("ACCESS_LOG_MAX_BODY", "2048"))
        req_body_preview = None
        content_type = request.headers.get("content-type", "")

        if capture_body:
            body = await request.body()
            preview = body[:max_bytes]
            if "application/json" in content_type:
                try:
                    js = json.loads(preview.decode("utf-8", errors="ignore"))
                    js = _redact_json(
                        js,
                        [
                            k
                            for k in os.getenv("ACCESS_LOG_REDACT_KEYS", "").split(",")
                            if k.strip()
                        ],
                    )
                    req_body_preview = js
                except Exception:
                    req_body_preview = preview.decode("utf-8", errors="ignore")
            else:
                req_body_preview = preview.decode("utf-8", errors="ignore")

            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive  # starlette internals; safe for this use

        t0 = time.perf_counter()
        try:
            response: Response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            dur_ms = round((time.perf_counter() - t0) * 1000, 2)
            client = request.client.host if request.client else None
            ua = request.headers.get("user-agent")

            record = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "request_id": rid,
                "method": method,
                "path": route_path,
                "query": dict(request.query_params),
                "status": status,
                "duration_ms": dur_ms,
                "client": client,
                "ua": ua,
                "headers": req_headers,
            }
            if capture_body:
                record["req_body_preview"] = req_body_preview

            ACCESS_LOG.info(json.dumps(record, ensure_ascii=False))

        if "x-request-id" not in response.headers:
            response.headers["X-Request-ID"] = rid
        return response

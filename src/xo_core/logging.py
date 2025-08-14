import json
import logging
import os
import sys
import time
import traceback
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional
from logging.handlers import TimedRotatingFileHandler

# Per-request correlation id context
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
route_var: ContextVar[Optional[str]] = ContextVar("route", default=None)
method_var: ContextVar[Optional[str]] = ContextVar("method", default=None)


def get_request_id() -> Optional[str]:
    return request_id_var.get()


def set_request_context(
    request_id: str, route: Optional[str], method: Optional[str]
) -> None:
    request_id_var.set(request_id)
    route_var.set(route)
    method_var.set(method)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": getattr(record, "ts", None)
            or time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = get_request_id()
        if rid:
            base["request_id"] = rid
        r = getattr(record, "route", None) or route_var.get()
        m = getattr(record, "method", None) or method_var.get()
        if r:
            base["route"] = r
        if m:
            base["method"] = m
        for key in ("path", "status_code", "duration_ms", "client", "extra"):
            val = getattr(record, key, None)
            if val is not None:
                base[key] = val
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            base["error"] = {
                "type": getattr(exc_type, "__name__", str(exc_type)),
                "message": str(exc_value),
                "stack": "".join(
                    traceback.format_exception(exc_type, exc_value, exc_tb)
                ),
            }
        return json.dumps(base, ensure_ascii=False)


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)

    # Build stdout and optional rotating file handlers
    for handler in _build_handlers():
        root.addHandler(handler)

    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def new_request_id() -> str:
    return str(uuid.uuid4())


def _build_handlers() -> list[logging.Handler]:
    fmt = JsonFormatter()
    handlers: list[logging.Handler] = []

    # STDOUT (default on)
    if os.getenv("LOG_TO_STDOUT", "1") not in ("0", "false", "False"):
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setFormatter(fmt)
        handlers.append(stdout_handler)

    # File rotate (optional)
    log_file = os.getenv("LOG_FILE")  # e.g., logs/xo-core.jsonl
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        when = os.getenv("LOG_ROTATE_WHEN", "midnight")
        backup = int(os.getenv("LOG_ROTATE_BACKUP", "14"))  # keep 14 days
        file_handler = TimedRotatingFileHandler(
            log_file,
            when=when,
            backupCount=backup,
            encoding="utf-8",
            utc=True,
        )
        file_handler.setFormatter(fmt)
        handlers.append(file_handler)

    return handlers

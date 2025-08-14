import os
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import yaml


API_KEY_REGISTRY: Dict[str, Any] = {}


def load_api_key_registry(path: Optional[str] = None) -> Dict[str, Any]:
    global API_KEY_REGISTRY
    if API_KEY_REGISTRY:
        return API_KEY_REGISTRY
    config_path = Path(path or os.getenv("API_KEYS_PATH", "config/api_keys.yml"))
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        API_KEY_REGISTRY = yaml.safe_load(f) or {}
    return API_KEY_REGISTRY


def rate_limit_key(request: Request) -> str:
    # Prefer API key header if present, else client IP
    api_key = request.headers.get("x-api-key")
    return api_key or get_remote_address(request)


def get_tier_for_request(request: Request) -> str:
    api_key = request.headers.get("x-api-key")
    registry = load_api_key_registry()
    if not api_key:
        return "free"
    return registry.get("keys", {}).get(api_key, "free")


def get_limit_for_tier(tier: str, path: Optional[str] = None) -> str:
    registry = load_api_key_registry()
    if path:
        path_overrides = registry.get("overrides", {}).get(path, {})
        if tier in path_overrides:
            return path_overrides[tier]
    return registry.get("tiers", {}).get(tier, {}).get("limit", "60/minute")


def build_limiter() -> Limiter:
    # Use Redis/Memcached/etc via limits storage URI if provided; else in-memory
    storage_uri = os.getenv("RATE_LIMIT_STORAGE_URI")  # e.g. "redis://localhost:6379/0"
    return Limiter(
        key_func=rate_limit_key,
        default_limits=[os.getenv("RATE_LIMIT_DEFAULT", "60/minute")],
        storage_uri=storage_uri,
        headers_enabled=True,  # add rate headers to responses
    )


def install_rate_limiting(app: FastAPI, limiter: Optional[Limiter] = None) -> Limiter:
    limiter = limiter or build_limiter()

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "ok": False,
                "error": "rate_limited",
                "detail": str(exc),
            },
        )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    return limiter

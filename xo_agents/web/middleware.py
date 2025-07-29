"""
XO Agents Web Middleware

Middleware for secret verification and request processing.
"""

import os
import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def verify_agent_secret(request: Request, call_next):
    """
    Middleware to verify X-Agent-Secret header for /agent/* endpoints.

    Only applies to /agent/* routes and logs if XO_AGENT_SECRET is missing.
    """
    # Only apply to /agent/* endpoints
    if not request.url.path.startswith("/agent/"):
        return await call_next(request)

    expected_secret = os.getenv("XO_AGENT_SECRET")
    actual_secret = request.headers.get("X-Agent-Secret")

    # Log if secret is missing (guardrail)
    if not expected_secret:
        logger.warning("XO_AGENT_SECRET environment variable not set")
        return await call_next(request)

    # Verify secret if provided
    if actual_secret != expected_secret:
        logger.warning(f"Invalid agent secret provided for {request.url.path}")
        raise HTTPException(status_code=403, detail="Forbidden: Invalid agent secret")

    return await call_next(request)


async def log_webhook_requests(request: Request, call_next):
    """
    Middleware to log webhook requests for debugging.
    """
    if request.url.path.startswith("/agent/"):
        logger.info(f"Webhook request: {request.method} {request.url.path}")

    response = await call_next(request)

    if request.url.path.startswith("/agent/"):
        logger.info(f"Webhook response: {response.status_code}")

    return response

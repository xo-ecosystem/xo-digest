"""
XO Agents API

Main FastAPI application with webhook router and middleware.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import the new modular webhook router
from .web.webhook_router import router as webhook_router
from .web.middleware import verify_agent_secret, log_webhook_requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="XO Agent API",
    version="1.0.0",
    description="XO Agent webhook system for task dispatching",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add custom middleware for agent secret verification and logging
@app.middleware("http")
async def agent_middleware(request: Request, call_next):
    """Combined middleware for agent endpoints."""
    # Log webhook requests
    response = await log_webhook_requests(request, call_next)

    # Verify agent secret for /agent/* endpoints
    if request.url.path.startswith("/agent/"):
        response = await verify_agent_secret(request, call_next)

    return response


# Include the webhook router
app.include_router(webhook_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "XO Agent API",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/agent/webhook",
            "test": "/agent/test",
            "tasks": "/agent/tasks",
            "health": "/agent/health",
            "echo": "/agent/echo",
        },
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Global health check."""
    return {"status": "healthy", "service": "XO Agent API"}

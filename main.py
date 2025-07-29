"""
XO Core Main Application

Main FastAPI application with webhook router integration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the new modular webhook router
from xo_agents.web.webhook_router import router as webhook_router

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="XO Core",
    version="1.0.0",
    description="XO Core system with agent webhook integration",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the webhook router
app.include_router(webhook_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "XO Core",
        "version": "1.0.0",
        "webhook_endpoints": {
            "webhook": "/agent/webhook",
            "test": "/agent/test",
            "tasks": "/agent/tasks",
            "health": "/agent/health",
        },
    }

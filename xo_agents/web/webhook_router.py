"""
XO Agents Webhook Router

FastAPI router for agent webhook endpoints with task dispatching.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from .tasks import (
    run_task,
    get_available_tasks,
    validate_task_request,
    TaskRequest,
    TaskResponse,
)
from .middleware import verify_agent_secret

logger = logging.getLogger(__name__)

# Create router with /agent prefix
router = APIRouter(prefix="/agent")


class WebhookPayload(BaseModel):
    """Webhook payload model for GitHub triggers."""

    task: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}


class EchoPayload(BaseModel):
    """Echo payload for debugging."""

    data: Dict[str, Any]


@router.post("/webhook")
async def receive_webhook(payload: WebhookPayload, request: Request):
    """
    Main webhook endpoint for task dispatching.

    Supports GitHub-triggered automation with task + args in JSON:
    {
      "task": "pulse.sync",
      "args": ["bundle_name"]
    }
    """
    logger.info(f"📥 Webhook received: {payload.task} with args={payload.args}")

    # Validate task request
    if not validate_task_request(payload.task, payload.args):
        raise HTTPException(
            status_code=400, detail=f"Invalid task request: {payload.task}"
        )

    # Execute task
    result = run_task(payload.task, payload.args, payload.kwargs)

    # Return response
    if result.status == "success":
        return {"status": "ok", "task": payload.task, "result": result.result}
    else:
        raise HTTPException(status_code=500, detail=f"Task failed: {result.error}")


@router.get("/test")
async def agent_test():
    """
    Test endpoint that returns available tasks and status.

    Used for health checks and task discovery.
    """
    tasks = get_available_tasks()
    return {
        "status": "alive",
        "available_tasks": list(tasks.keys()),
        "task_descriptions": {
            task: config["description"] for task, config in tasks.items()
        },
    }


@router.post("/echo")
async def echo_webhook(payload: EchoPayload):
    """
    Echo endpoint for debugging webhook payloads.

    Returns the raw POST payload for testing and debugging.
    """
    logger.info(f"🔊 Echo request: {payload.data}")
    return {
        "status": "echo",
        "received": payload.data,
        "timestamp": "2025-01-27T00:00:00Z",  # Could use actual timestamp
    }


@router.get("/tasks")
async def list_tasks():
    """
    List all available tasks with descriptions and expected arguments.
    """
    tasks = get_available_tasks()
    return {"tasks": tasks, "count": len(tasks)}


@router.post("/run-task")
async def run_task_endpoint(payload: TaskRequest):
    """
    Alternative task execution endpoint with more detailed response.

    Returns TaskResponse with status, result, and error information.
    """
    logger.info(f"🚀 Run task request: {payload.task}")

    # Validate task
    if not validate_task_request(payload.task, payload.args):
        raise HTTPException(status_code=400, detail=f"Invalid task: {payload.task}")

    # Execute task
    result = run_task(payload.task, payload.args, payload.kwargs)

    # Return detailed response
    return result


@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "xo-agents-webhook", "version": "1.0.0"}


# Note: Exception handlers should be added to the main FastAPI app, not the router
# These are handled by the main application in api.py and main.py

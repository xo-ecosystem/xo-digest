"""
XO Vault API Server
Provides REST API endpoints for vault task execution
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import subprocess
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="XO Vault API",
    description="API for executing XO Vault tasks",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    params: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def execute_fab_task(task_name: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Execute a fabric task and return the result"""
    try:
        # Build the command
        cmd = ["xo-fab", task_name]
        
        # Add parameters
        for key, value in params.items():
            if isinstance(value, bool):
                if value:
                    cmd.append(f"--{key}")
            else:
                cmd.append(f"--{key}={value}")
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Task {task_name} executed successfully",
                "data": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            }
        else:
            return {
                "success": False,
                "message": f"Task {task_name} failed",
                "error": result.stderr or "Unknown error",
                "data": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            }
    except Exception as e:
        logger.error(f"Error executing task {task_name}: {e}")
        return {
            "success": False,
            "message": f"Error executing task {task_name}",
            "error": str(e)
        }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "XO Vault API Server",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/api/vault/status")
async def get_vault_status():
    """Get vault status"""
    result = execute_fab_task("cosmos.vault-agent-status")
    return TaskResponse(**result)

@app.get("/api/vault/storage")
async def get_storage_status():
    """Get storage status"""
    result = execute_fab_task("storage.status")
    return TaskResponse(**result)

@app.get("/api/vault/health")
async def get_backend_health():
    """Get backend health"""
    result = execute_fab_task("backend.check-health")
    return TaskResponse(**result)

@app.post("/api/vault/execute")
async def execute_task(request: TaskRequest):
    """Execute a vault task"""
    logger.info(f"Executing task: {request.task} with params: {request.params}")
    
    result = execute_fab_task(request.task, request.params)
    return TaskResponse(**result)

@app.post("/api/vault/snapshot")
async def create_snapshot():
    """Create a system snapshot"""
    result = execute_fab_task("seal.system-snapshot")
    return TaskResponse(**result)

@app.post("/api/vault/setup")
async def setup_agent(keys: int = 5):
    """Setup vault agent"""
    result = execute_fab_task("cosmos.vault-agent-setup", {"keys": keys})
    return TaskResponse(**result)

@app.post("/api/vault/loop")
async def initiate_loop(agents: str = "agent0,agentx,agentz"):
    """Initiate agent loop"""
    result = execute_fab_task("cosmos.initiate-loop", {"agents": agents})
    return TaskResponse(**result)

@app.post("/api/vault/route")
async def route_smart(path: str, drop: Optional[str] = None):
    """Route files smart"""
    params = {"path": path}
    if drop:
        params["drop"] = drop
    result = execute_fab_task("storage.route-smart", params)
    return TaskResponse(**result)

@app.post("/api/vault/sync")
async def sync_manifest():
    """Sync spec manifest"""
    result = execute_fab_task("spec.sync-manifest")
    return TaskResponse(**result)

@app.get("/api/vault/mesh")
async def get_agent_mesh():
    """Get agent mesh map"""
    result = execute_fab_task("backend.agent-mesh-map")
    return TaskResponse(**result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
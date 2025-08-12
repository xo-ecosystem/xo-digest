"""
XO Agents API

Main FastAPI application with webhook router and authentication.
"""

import logging
import json
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

# Import the routers
from .web.webhook_router import router as webhook_router
from .web.handles_router import router as handles_router
from .web import sign_router as _sign_router
from .web.oidc import verify_request

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
    allow_origins=[
        o.strip()
        for o in os.getenv("XO_CORS", "http://localhost:5173").split(",")
        if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Note: Authentication is enforced via FastAPI dependencies using verify_request.


# Include routers under /agent and protect them with OIDC (with legacy fallback inside verify_request)
app.include_router(webhook_router, dependencies=[Depends(verify_request)])
app.include_router(
    handles_router, prefix="/agent", dependencies=[Depends(verify_request)]
)
app.include_router(_sign_router.router)


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


# --- Secure report server: GET /vault/decoded/{run_id}/index.html ---
DECODE_BASE = Path(os.path.expanduser("~/.config/xo-core/decoded")).resolve()
ALLOWED_FROM_WEB = set(os.getenv("XO_WEB_ALLOWLIST", "brie").split(","))


@app.get("/vault/decoded/{run_id}/index.html")
async def get_decode_report(
    run_id: str, request: Request, handle: str = "brie", _auth=Depends(verify_request)
):
    # Enforce handle allowlist and role-based access (hard brie-only gate)
    if handle not in ALLOWED_FROM_WEB:
        raise HTTPException(status_code=403, detail="handle not allowed")
    roles = (_auth or {}).get("roles", [])
    if "brie" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: brie role required")
    report = (DECODE_BASE / run_id / "index.html").resolve()
    if not report.is_file() or DECODE_BASE not in report.parents:
        raise HTTPException(status_code=404, detail="report not found")
    return FileResponse(str(report), media_type="text/html")


# --- Decode UI: simple single-file HTML ---
_UI_PATH = Path(__file__).parent / "web" / "ui_decode.html"


@app.get("/vault/ui")
async def decode_ui(request: Request):
    if not _UI_PATH.is_file():
        raise HTTPException(status_code=404, detail="ui not found")
    template_html = _UI_PATH.read_text(encoding="utf-8")
    # Build config for client-side OIDC
    redirect_default = f"{request.url.scheme}://{request.url.netloc}/vault/ui"
    cfg = {
        "issuer": os.getenv("XO_OIDC_ISSUER", ""),
        "audience": os.getenv("XO_OIDC_AUDIENCE", ""),
        # Accept either XO_OIDC_CLIENT_ID_SPA or XO_OIDC_CLIENT_ID
        "clientId": os.getenv(
            "XO_OIDC_CLIENT_ID_SPA", os.getenv("XO_OIDC_CLIENT_ID", "")
        ),
        "redirectUri": os.getenv("XO_OIDC_REDIRECT_URI", redirect_default),
        "allowLegacy": os.getenv("XO_ALLOW_LEGACY_SECRET", "0") == "1",
    }
    html = template_html.replace("__XO_CFG__", json.dumps(cfg))
    return HTMLResponse(html)


@app.get("/agent/decode/runs")
async def list_decode_runs(
    request: Request, limit: int = 20, _auth=Depends(verify_request)
):
    if not DECODE_BASE.exists():
        return {"runs": []}
    runs = []
    try:
        for entry in DECODE_BASE.iterdir():
            if entry.is_dir() and (entry / "index.html").exists():
                runs.append(
                    {
                        "run_id": entry.name,
                        "index_html": f"/vault/decoded/{entry.name}/index.html",
                        "mtime": (entry / "index.html").stat().st_mtime,
                    }
                )
        runs.sort(key=lambda x: x["mtime"], reverse=True)
        if limit and limit > 0:
            runs = runs[:limit]
        for r in runs:
            r.pop("mtime", None)
        return {"runs": runs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to enumerate runs: {e}")

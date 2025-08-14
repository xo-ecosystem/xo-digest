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
import hmac, hashlib, time, base64

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


def _sign_payload(secret: str, payload: str) -> str:
    mac = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")


def _verify_sig(secret: str, payload: str, sig: str) -> bool:
    try:
        expected = _sign_payload(secret, payload)
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False


def _b64url_decode(data: str) -> bytes:
    # add padding
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


@app.post("/agent/decode/sign-url")
async def sign_decode_url(request: Request, _auth=Depends(verify_request)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid json")
    run_id = (body.get("run_id") or "").strip()
    ttl_s = int(body.get("ttl_s") or 600)
    if not run_id:
        raise HTTPException(status_code=400, detail="missing run_id")
    secret = os.getenv("XO_AGENT_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="signing unavailable")
    exp = int(time.time()) + max(60, min(ttl_s, 24 * 3600))
    payload = f"{run_id}:{exp}"
    sig = _sign_payload(secret, payload)
    return {
        "url": f"/vault/decoded/{run_id}/index.html?sig={sig}&exp={exp}",
        "expires_at": exp,
    }


@app.get("/vault/decoded/{run_id}/index.html")
async def get_decode_report(run_id: str, request: Request, handle: str = "brie"):
    # Signed URL mode
    sig = request.query_params.get("sig")
    exp = request.query_params.get("exp")
    if sig and exp:
        secret = os.getenv("XO_AGENT_SECRET")
        if not secret:
            raise HTTPException(status_code=503, detail="signing unavailable")
        payload = f"{run_id}:{exp}"
        if not _verify_sig(secret, payload, sig):
            raise HTTPException(status_code=401, detail="bad signature")
        try:
            if int(exp) < int(time.time()):
                raise HTTPException(status_code=401, detail="expired")
        except ValueError:
            raise HTTPException(status_code=400, detail="bad exp")
        report = (DECODE_BASE / run_id / "index.html").resolve()
        if not report.is_file() or DECODE_BASE not in report.parents:
            raise HTTPException(status_code=404, detail="report not found")
        return FileResponse(str(report), media_type="text/html")

    # Protected mode via OIDC/legacy secret
    auth = await verify_request(request)
    if handle not in ALLOWED_FROM_WEB:
        raise HTTPException(status_code=403, detail="handle not allowed")
    roles = (auth or {}).get("roles", [])
    if "brie" not in roles:
        raise HTTPException(status_code=403, detail="forbidden: brie role required")
    report = (DECODE_BASE / run_id / "index.html").resolve()
    if not report.is_file() or DECODE_BASE not in report.parents:
        raise HTTPException(status_code=404, detail="report not found")
    return FileResponse(str(report), media_type="text/html")


@app.get("/vault/decoded/{run_id}/{subpath:path}")
async def get_decode_asset(
    run_id: str, subpath: str, request: Request, handle: str = "brie"
):
    # Signed URL mode for assets: require same sig/exp
    sig = request.query_params.get("sig")
    exp = request.query_params.get("exp")
    if sig and exp:
        secret = os.getenv("XO_AGENT_SECRET")
        if not secret:
            raise HTTPException(status_code=503, detail="signing unavailable")
        payload = f"{run_id}:{exp}"
        if not _verify_sig(secret, payload, sig):
            raise HTTPException(status_code=401, detail="bad signature")
        try:
            if int(exp) < int(time.time()):
                raise HTTPException(status_code=401, detail="expired")
        except ValueError:
            raise HTTPException(status_code=400, detail="bad exp")
        target = (DECODE_BASE / run_id / subpath).resolve()
        if not target.is_file() or (DECODE_BASE / run_id) not in target.parents:
            raise HTTPException(status_code=404, detail="not found")
        return FileResponse(str(target))

    # Protected mode via OIDC/legacy secret
    await verify_request(request)
    if handle not in ALLOWED_FROM_WEB:
        raise HTTPException(status_code=403, detail="handle not allowed")
    target = (DECODE_BASE / run_id / subpath).resolve()
    if not target.is_file() or (DECODE_BASE / run_id) not in target.parents:
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(str(target))


# --- Decode UI: simple single-file HTML ---
_UI_PATH = Path(__file__).parent / "web" / "ui_decode.html"
_UI_BRIE = Path(__file__).parent / "web" / "ui_brie.html"


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


@app.get("/vault/ui/brie")
async def brie_ui():
    if _UI_BRIE.is_file():
        return FileResponse(str(_UI_BRIE), media_type="text/html")
    raise HTTPException(status_code=404, detail="ui not found")

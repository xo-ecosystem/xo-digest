# src/xo_agent/webhooks/github.py
import hmac, hashlib, json, logging, os
from fastapi import APIRouter, Header, HTTPException, Request
from starlette.responses import JSONResponse

router = APIRouter()
log = logging.getLogger("github-webhook")

GH_WEBHOOK_SECRET = os.getenv("GH_WEBHOOK_SECRET", "").encode()

def verify_signature(body: bytes, signature_header: str | None) -> None:
    if not GH_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="GH_WEBHOOK_SECRET not set")
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(status_code=400, detail="Missing or bad X-Hub-Signature-256")
    digest = hmac.new(GH_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    # constant-time compare
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=None),
    x_github_delivery: str = Header(default="")
):
    raw = await request.body()
    verify_signature(raw, x_hub_signature_256)

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Handle the "ping" event immediately
    if x_github_event == "ping":
        return JSONResponse({"ok": True, "pong": True, "delivery": x_github_delivery})

    # Minimal router: add what you need
    if x_github_event == "push":
        ref = payload.get("ref")
        repo = payload.get("repository", {}).get("full_name")
        head = payload.get("after")
        log.info(f"[push] {repo}@{ref} -> {head}")
        # 👉 trigger your XO workflows here (examples below)
        # await agent_dispatch("deploy.guard", {"repo": repo, "ref": ref, "sha": head})
        return {"ok": True, "handled": "push"}

    if x_github_event == "pull_request":
        action = payload.get("action")
        repo = payload.get("repository", {}).get("full_name")
        pr = payload.get("number")
        log.info(f"[pr] {repo} #{pr} {action}")
        # await agent_dispatch("pr.guard", {"repo": repo, "number": pr, "action": action})
        return {"ok": True, "handled": "pull_request"}

    if x_github_event == "repository":
        action = payload.get("action")
        name = payload.get("repository", {}).get("full_name")
        log.info(f"[repo] {name} {action}")
        return {"ok": True, "handled": "repository"}

    # Default: accept but note unhandled types
    log.info(f"[{x_github_event}] delivery={x_github_delivery} (no handler)")
    return {"ok": True, "handled": False, "event": x_github_event}

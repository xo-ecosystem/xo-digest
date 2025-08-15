import hmac, hashlib, json, os, logging
from fastapi import APIRouter, Header, HTTPException, Request
from starlette.responses import JSONResponse

router = APIRouter()
log = logging.getLogger("github-webhook")

# Set in environment or .env.local / .env.production
GH_WEBHOOK_SECRET = os.getenv("GH_WEBHOOK_SECRET", "").encode()


def _verify_signature(body: bytes, signature_header: str | None) -> None:
    if not GH_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="GH_WEBHOOK_SECRET not set")
    if not signature_header or not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=400, detail="Missing or bad X-Hub-Signature-256"
        )
    digest = hmac.new(GH_WEBHOOK_SECRET, body, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=None),
    x_github_delivery: str = Header(default=""),
):
    raw = await request.body()
    _verify_signature(raw, x_hub_signature_256)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if x_github_event == "ping":
        return JSONResponse({"ok": True, "pong": True, "delivery": x_github_delivery})

    if x_github_event == "push":
        ref = payload.get("ref")
        repo = payload.get("repository", {}).get("full_name")
        sha = payload.get("after")
        log.info(f"[push] {repo}@{ref} -> {sha}")
        # Example: only act on main/staging
        if ref in ("refs/heads/main", "refs/heads/staging"):
            # TODO: wire into your deploy hooks (fabric/agent)
            # await agent_dispatch("deploy.prod" if ref.endswith("/main") else "deploy.staging", payload)
            pass
        return {"ok": True, "handled": "push", "ref": ref}

    # Unhandled → accept quietly
    log.info(f"[{x_github_event}] delivery={x_github_delivery} (no handler)")
    return {"ok": True, "handled": False, "event": x_github_event}

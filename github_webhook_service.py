import hmac, hashlib, json, os
from fastapi import FastAPI, Request, Header, HTTPException
from starlette.responses import JSONResponse

app = FastAPI()
SECRET = os.getenv("GH_WEBHOOK_SECRET", "").encode()


def verify(raw: bytes, sig: str | None):
    if not SECRET:
        raise HTTPException(500, "GH_WEBHOOK_SECRET not set")
    if not sig or not sig.startswith("sha256="):
        raise HTTPException(400, "Bad signature")
    good = "sha256=" + hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(good, sig):
        raise HTTPException(401, "Invalid signature")


@app.post("/postreceive")
async def postreceive(
    request: Request,
    x_github_event: str = Header(default=""),
    x_hub_signature_256: str = Header(default=None),
):
    raw = await request.body()
    verify(raw, x_hub_signature_256)
    payload = json.loads(raw.decode("utf-8"))
    if x_github_event == "ping":
        return {"ok": True, "pong": True}
    # …same handlers as Option 1…
    return JSONResponse({"ok": True, "event": x_github_event})

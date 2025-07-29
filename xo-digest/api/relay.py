

from fastapi import APIRouter, Request, Header, HTTPException
from starlette.responses import JSONResponse
import os

router = APIRouter()

@router.post("/api/relay")
async def sanity_relay(
    request: Request,
    x_sanity_signature: str = Header(None),
):
    secret = os.getenv("SANITY_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Missing secret")

    # Read the raw body
    body = await request.body()

    # Here, normally you'd verify the signature with HMAC + secret
    # Skipping for now — consider adding hmac.compare_digest() later
    if not x_sanity_signature:
        raise HTTPException(status_code=400, detail="Missing signature header")

    print("✅ Sanity webhook received:", body.decode())

    # Placeholder: add logic to log, parse, or forward this
    return JSONResponse(content={"status": "received"}, status_code=200)
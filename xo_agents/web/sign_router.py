from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import base64
import re
from xo_agents.web.oidc import verify_request
from xo_core.crypto.signer import get_signer


router = APIRouter(
    prefix="/agent/sign", tags=["sign"], dependencies=[Depends(verify_request)]
)


class SignReq(BaseModel):
    message: str  # raw string or base64:... for binary
    encoding: str = "utf-8"  # "utf-8" | "base64"


def _to_bytes(s: str, enc: str) -> bytes:
    if enc == "base64":
        return base64.b64decode(s, validate=True)
    return s.encode("utf-8")


def _is_risky(b: bytes) -> bool:
    t = b.decode("utf-8", errors="ignore")
    return bool(
        re.search(r"(PRIVATE\s+KEY|MNEMONIC|SECRET|TOKEN|PASSWORD|BEARER\s+)", t, re.I)
    )


@router.get("/status")
def status():
    s = get_signer()
    return {"backend": s.name, "address": s.address()}


@router.post("")
def sign(req: SignReq, _: Request):
    b = _to_bytes(req.message, req.encoding)
    if len(b) > 64 * 1024:
        raise HTTPException(413, "message too large")
    if _is_risky(b):
        raise HTTPException(400, "message contains sensitive markers; refused")
    s = get_signer()
    out = s.sign_message(b)
    return {"ok": True, "backend": s.name, **out}

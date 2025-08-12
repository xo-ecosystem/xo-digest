from fastapi import APIRouter, HTTPException, Request, Depends, Body
from .oidc import verify_request

# Lazy, graceful handles imports
FEATURE_ENABLED = False
ALLOWLIST = {"brie"}
CLAIM_TTL_MIN = 30
_handles_ok = False
try:
    from xo_core.handles.config import (
        FEATURE_ENABLED as _FEAT,
        ALLOWLIST as _AL,
        CLAIM_TTL_MIN as _TTL,
    )
    from xo_core.handles.registry import (
        HandleClaim,
        save_claim,
        load_claim,
        write_record,
        read_record,
    )
    from xo_core.handles.verify import new_challenge, verify_wallet_sig, mark_verified
    from xo_core.handles.signer import sign_record

    FEATURE_ENABLED, ALLOWLIST, CLAIM_TTL_MIN = _FEAT, _AL, _TTL
    _handles_ok = True
except Exception:
    _handles_ok = False

router = APIRouter(
    prefix="/handles", tags=["handles"], dependencies=[Depends(verify_request)]
)


@router.get("/{handle}")
async def fetch_handle(handle: str):
    try:
        rec = read_record(handle)
    except Exception:
        raise HTTPException(status_code=503, detail="handle module unavailable")
    if not rec:
        raise HTTPException(404, "handle not found")
    return rec


@router.post("/claim")
async def claim_handle(req: Request, body: dict = Body(...)):
    global _handles_ok
    if not _handles_ok:
        try:
            from xo_core.handles.config import (
                FEATURE_ENABLED as _FEAT,
                ALLOWLIST as _AL,
                CLAIM_TTL_MIN as _TTL,
            )
            from xo_core.handles.registry import HandleClaim, save_claim
            from xo_core.handles.verify import new_challenge

            globals().update(
                {
                    "FEATURE_ENABLED": _FEAT,
                    "ALLOWLIST": _AL,
                    "CLAIM_TTL_MIN": _TTL,
                    "HandleClaim": HandleClaim,
                    "save_claim": save_claim,
                    "new_challenge": new_challenge,
                }
            )
            _handles_ok = True
        except Exception:
            raise HTTPException(status_code=503, detail="handle module unavailable")
    if not FEATURE_ENABLED:
        raise HTTPException(503, "feature disabled")
    data = body
    handle = (data.get("handle") or "").strip().lower()
    method = (data.get("method") or "").strip().lower()  # "wallet" | "token"
    if handle not in ALLOWLIST:
        raise HTTPException(403, "not allowlisted")
    ch = new_challenge()
    claim = HandleClaim(
        handle=handle,
        method=method,
        challenge=ch,
        ttl_min=CLAIM_TTL_MIN,
        created_at=__import__("time").time(),
    )
    save_claim(claim)
    return {
        "ok": True,
        "handle": handle,
        "challenge": ch,
        "method": method,
        "ttl_min": CLAIM_TTL_MIN,
    }


@router.post("/verify")
async def verify_handle(req: Request, body: dict = Body(...)):
    try:
        from xo_core.handles.registry import load_claim
        from xo_core.handles.verify import verify_wallet_sig, mark_verified
    except Exception:
        raise HTTPException(status_code=503, detail="handle module unavailable")
    data = body
    handle = (data.get("handle") or "").strip().lower()
    claim = load_claim(handle)
    if not claim or claim.expired():
        raise HTTPException(400, "no active claim or expired")
    if claim.method == "wallet":
        sig = data.get("signature")
        addr = verify_wallet_sig(claim.challenge, sig)
        if not addr:
            raise HTTPException(400, "bad signature")
        claim = mark_verified(claim, address=addr)
    elif claim.method == "token":
        if data.get("token") != claim.challenge:
            raise HTTPException(400, "bad token")
        claim = mark_verified(claim)
    else:
        raise HTTPException(400, "unsupported method")
    return {"ok": True, "status": claim.status, "address": claim.address}


@router.post("/activate")
async def activate_handle(req: Request, body: dict = Body(...)):
    try:
        from xo_core.handles.registry import load_claim, write_record
        from xo_core.handles.signer import sign_record
    except Exception:
        raise HTTPException(status_code=503, detail="handle module unavailable")
    data = body
    handle = (data.get("handle") or "").strip().lower()
    display = data.get("display", "Brie")
    claim = load_claim(handle)
    if not claim or claim.status != "verified":
        raise HTTPException(400, "claim not verified")
    record = {
        "handle": handle,
        "display": display,
        "address": claim.address,
        "state": "active",
        "meta": {"created_by": "handle-claim", "methods": claim.method},
    }
    return sign_record(write_record(record))

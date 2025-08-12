import json
from xo_core.handles.registry import HandleClaim, save_claim, load_claim
from xo_core.handles.verify import new_challenge, mark_verified
from xo_core.handles.signer import sign_record


def test_claim_roundtrip():
    ch = new_challenge()
    c = HandleClaim(
        handle="brie", method="token", challenge=ch, ttl_min=30, created_at=0
    )
    save_claim(c)
    c2 = load_claim("brie")
    assert c2 and c2.challenge == ch
    mark_verified(c2)
    rec = {"handle": "brie", "display": "Brie", "address": None, "state": "active"}
    rec = sign_record(rec)
    assert "signature" in rec and "record_hash" in rec

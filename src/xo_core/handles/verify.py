from __future__ import annotations
import os, secrets

try:
    from eth_account.messages import encode_defunct  # type: ignore
    from eth_account import Account  # type: ignore
except Exception:  # pragma: no cover - optional dependency for tests
    encode_defunct = None
    Account = None
from .registry import HandleClaim, save_claim


def new_challenge() -> str:
    return secrets.token_urlsafe(24)


def verify_wallet_sig(challenge: str, signature: str) -> str | None:
    try:
        if not encode_defunct or not Account:
            return None
        msg = encode_defunct(text=challenge)
        addr = Account.recover_message(msg, signature=signature)
        return addr
    except Exception:
        return None


def generate_maintainer_token() -> str:
    # Maintainer runs this locally to create a one-time token to share out of band
    return secrets.token_urlsafe(16)


def mark_verified(claim: HandleClaim, address: str | None = None) -> HandleClaim:
    claim.status = "verified"
    claim.address = address
    save_claim(claim)
    return claim

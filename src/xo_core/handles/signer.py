import json, time
from .registry import sha256


def sign_record(payload: dict) -> dict:
    # TODO: wire to Vault signing key if available
    payload = dict(payload)
    payload["signed_at"] = int(time.time())
    payload["record_hash"] = sha256(json.dumps(payload, sort_keys=True).encode())
    payload["signature"] = f"dev-signature::{payload['record_hash']}"
    return payload

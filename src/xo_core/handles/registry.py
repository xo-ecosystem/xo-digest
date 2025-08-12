from __future__ import annotations
import time, json, os, hashlib, uuid
from pathlib import Path
from dataclasses import dataclass, asdict
from .config import REGISTRY_DIR, VAULT_OUT_DIR

Path(REGISTRY_DIR).mkdir(parents=True, exist_ok=True)
Path(VAULT_OUT_DIR).mkdir(parents=True, exist_ok=True)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class HandleClaim:
    handle: str
    method: str  # "wallet" | "token"
    challenge: str
    created_at: float
    ttl_min: int
    status: str = "pending"  # pending | verified | activated
    address: str | None = None  # eth addr if wallet method

    def expired(self) -> bool:
        return (time.time() - self.created_at) > (self.ttl_min * 60)


def _claims_path(handle: str) -> Path:
    return Path(REGISTRY_DIR) / f"{handle}.claim.json"


def _record_path(handle: str) -> Path:
    return Path(VAULT_OUT_DIR) / f"{handle}.handle.json"


def save_claim(c: HandleClaim) -> None:
    _claims_path(c.handle).write_text(json.dumps(asdict(c), indent=2))


def load_claim(handle: str) -> HandleClaim | None:
    p = _claims_path(handle)
    if not p.exists():
        return None
    obj = json.loads(p.read_text())
    return HandleClaim(**obj)


def write_record(record: dict) -> dict:
    # store signed record (signature added by signer util)
    p = _record_path(record["handle"])
    p.write_text(json.dumps(record, indent=2))
    return record


def read_record(handle: str) -> dict | None:
    p = _record_path(handle)
    if not p.exists():
        return None
    return json.loads(p.read_text())

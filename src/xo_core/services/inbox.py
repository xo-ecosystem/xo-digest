import os
from typing import List, Dict


def add_message(data: dict) -> None:
    # TODO: connect to Vault or persistent store
    _MESSAGES.append(data)
    print("[inbox.add_message]", data)


def list_messages() -> list:
    # TODO: load from Vault or persistent store
    return _MESSAGES


def get_messages() -> list:
    """Alias for list_messages for external callers."""
    return list_messages()


from .inbox_store import append as store_append, latest as store_latest


def get_latest_inbox_messages(drop_id: str, limit: int = 10) -> List[Dict]:
    return _with_permalinks(drop_id, store_latest(drop_id, limit))


def append_inbox_message(drop_id: str, user: str, msg: str) -> Dict:
    return store_append(drop_id, user, msg)


def _vault_base() -> str:
    return os.getenv("XO_VAULT_BASE_URL", "https://vault.xo.eco").rstrip("/")


def make_vault_inbox_url(drop_id: str) -> str:
    base = _vault_base()
    return f"{base}/inbox/{drop_id}"


def make_vault_message_url(drop_id: str, mid: str) -> str:
    base = _vault_base()
    return f"{base}/inbox/{drop_id}/m/{mid}"


def _with_permalinks(drop_id: str, rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    for i, r in enumerate(rows):
        rid = r.get("id") or r.get("ts") or str(i)
        r2 = {**r, "id": str(rid), "permalink": f"/inbox/{drop_id}/m/{rid}"}
        out.append(r2)
    return out

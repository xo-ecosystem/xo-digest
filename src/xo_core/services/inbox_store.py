import os
import json
import datetime
import io
from typing import List, Dict

# CONFIG
INBOX_DIR = os.getenv("XO_INBOX_DIR", os.path.abspath("data/inbox"))
INBOX_PREFIX = os.getenv("XO_INBOX_PREFIX", "inbox")  # used for Vault paths


def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# ---- Optional Vault adapter (duck-typed) ----
def _get_vault():
    """
    Try to import a Vault client if present.
    Expecting something like:
      from xo_core.vault.client import get_client
      client.get_text(path) -> str
      client.put_text(path, str) -> None
    """
    try:
        from xo_core.vault.client import get_client  # type: ignore

        return get_client()
    except Exception:
        return None


_VAULT = _get_vault()


def _vault_path(drop_id: str) -> str:
    # e.g. "inbox/message_bottle.jsonl"
    return f"{INBOX_PREFIX}/{drop_id}.jsonl"


# ---- Disk backend ----
def _disk_path(drop_id: str) -> str:
    return os.path.join(INBOX_DIR, f"{drop_id}.jsonl")


def _read_disk_lines(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    items: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items


def _append_disk(path: str, obj: Dict) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ---- Vault backend ----
def _read_vault_lines(vpath: str) -> List[Dict]:
    txt = _VAULT.get_text(vpath)
    if not txt:
        return []
    items: List[Dict] = []
    for line in io.StringIO(txt):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items


def _append_vault(vpath: str, obj: Dict) -> None:
    try:
        txt = _VAULT.get_text(vpath) or ""
    except Exception:
        txt = ""
    buf = io.StringIO()
    if txt:
        buf.write(txt.rstrip("\n") + "\n")
    buf.write(json.dumps(obj, ensure_ascii=False) + "\n")
    _VAULT.put_text(vpath, buf.getvalue())


# ---- Public API ----
def append(drop_id: str, user: str, msg: str) -> Dict:
    entry = {"user": user, "msg": msg, "ts": _now_iso(), "drop": drop_id}
    if _VAULT:
        _append_vault(_vault_path(drop_id), entry)
    else:
        _append_disk(_disk_path(drop_id), entry)
    return entry


def latest(drop_id: str, limit: int = 5) -> List[Dict]:
    items: List[Dict]
    if _VAULT:
        items = _read_vault_lines(_vault_path(drop_id))
    else:
        items = _read_disk_lines(_disk_path(drop_id))
    return list(reversed(items[-limit:]))

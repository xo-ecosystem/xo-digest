from invoke import Collection
from xo_core.fab_tasks.vault import digest

ns = Collection("vault")
ns.add_collection(digest.ns, name="digest")


def get_trust_state(sha256: str, context: str = "manual") -> dict:
    """Return minimal trust state for a given sha256.

    Stub implementation until wired to XO Ledger / Aether Relayer.
    """
    return {"state": "unknown", "sha256": sha256, "context": context}

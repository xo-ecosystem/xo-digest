# xo_core.vault.utils

def pin_to_ipfs(filepath, metadata=None):
    """Stub for IPFS pinning utility"""
    print(f"📌 [stub] Pinning {filepath} to IPFS...")
    return {"cid": "stub-cid", "url": f"ipfs://stub-cid/{filepath}"}

def log_status(message, level="info"):
    """Stub for logging to Vault or console"""
    print(f"[{level.upper()}] {message}")

__all__ = ["pin_to_ipfs", "log_status"]
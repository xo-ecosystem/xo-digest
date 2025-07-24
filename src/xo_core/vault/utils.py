import os
import requests
from pathlib import Path

# xo_core.vault.utils

def pin_to_ipfs(filepath, metadata=None):
    """Stub for IPFS pinning utility"""
    print(f"📌 [stub] Pinning {filepath} to IPFS...")
    return {"cid": "stub-cid", "url": f"ipfs://stub-cid/{filepath}"}

def log_status(message, level="info"):
    """Stub for logging to Vault or console"""
    print(f"[{level.upper()}] {message}")


def vault_status():
    """Check if Vault is sealed or available"""
    vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    try:
        resp = requests.get(f"{vault_addr}/v1/sys/seal-status", timeout=2)
        if resp.ok:
            data = resp.json()
            sealed = data.get("sealed", True)
            print("🔐 Vault is", "SEALED" if sealed else "UNSEALED")
            return not sealed
        else:
            print(f"❌ Vault health check failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking Vault status: {e}")
        return False

def vault_pull_secrets():
    """Try to pull Vault secrets from GitHub CLI or local encrypted file."""
    import subprocess
    import json
    vault_keys = []

    # Try GitHub CLI first
    try:
        result = subprocess.run(["gh", "secret", "list", "--repo", "xo-ecosystem/xo-core", "--json", "name"], capture_output=True, text=True)
        if result.returncode == 0:
            print("📥 GitHub Secrets found:")
            names = json.loads(result.stdout)
            for i in range(1, 4):
                key = f"VAULT_UNSEAL_KEY_{i}"
                value_result = subprocess.run(["gh", "secret", "view", key, "--repo", "xo-ecosystem/xo-core", "--json", "value"], capture_output=True, text=True)
                if value_result.returncode == 0:
                    val = json.loads(value_result.stdout)["value"]
                    os.environ[key] = val
                    print(f"✅ Loaded {key}")
                    vault_keys.append(val)
                else:
                    print(f"⚠️ Could not retrieve {key}")
        else:
            print("⚠️ GitHub CLI failed to list secrets.")
    except FileNotFoundError:
        print("⚠️ GitHub CLI (gh) not installed. Skipping...")

    # Fallback: try local vault/.keys.enc
    if not vault_keys:
        enc_path = Path("vault/.keys.enc")
        if enc_path.exists():
            print("🔐 Reading keys from vault/.keys.enc (stub logic)")
            # Add actual decryption here if required
            with open(enc_path, "r") as f:
                lines = f.readlines()
            for i, line in enumerate(lines[:3]):
                key = f"VAULT_UNSEAL_KEY_{i+1}"
                os.environ[key] = line.strip()
                print(f"✅ Loaded {key} from file")
        else:
            print("❌ No fallback keyfile found at vault/.keys.enc")

    if not vault_keys and not Path("vault/.keys.enc").exists():
        print("❌ No unseal keys loaded.")

__all__ = ["pin_to_ipfs", "log_status", "vault_status", "vault_pull_secrets"]
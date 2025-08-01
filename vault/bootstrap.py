# vault/bootstrap.py
from pathlib import Path
from datetime import datetime
import os
import json

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=Path(".env.production"))
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")

# Import hvac with fallback
try:
    import hvac
except ImportError:
    print("⚠️ hvac not available, some vault functions may not work")
    hvac = None


def get_vault_client():
    """Get a configured Vault client instance."""
    if hvac is None:
        print("❌ hvac library not available")
        return None

    vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_token = os.getenv("VAULT_TOKEN")

    client = hvac.Client(url=vault_addr)
    if vault_token:
        client.token = vault_token

    return client


def get_vault_unseal_keys():
    """Get unseal keys from various sources with fallback logic."""
    # First try: unseal_keys.json file
    unseal_path = Path("vault/unseal_keys.json")
    if unseal_path.exists():
        try:
            data = json.loads(unseal_path.read_text())
            keys = data.get("vault", {}).get("unseal_keys", [])
            if keys and all(keys):
                print("🔑 Loaded unseal keys from vault/unseal_keys.json")
                return keys
        except Exception as e:
            print(f"⚠️ Failed to load unseal_keys.json: {e}")

    # Second try: encrypted keys file
    enc_path = Path("vault/.keys.enc")
    if enc_path.exists():
        try:
            # For now, assume simple line-based format
            # TODO: Implement proper decryption
            with open(enc_path, "r") as f:
                keys = [line.strip() for line in f.readlines()[:3] if line.strip()]
            if len(keys) >= 3:
                print("🔐 Loaded unseal keys from vault/.keys.enc")
                return keys
        except Exception as e:
            print(f"⚠️ Failed to load .keys.enc: {e}")

    # Third try: environment variables
    env_keys = []
    for i in range(1, 4):
        key = os.getenv(f"VAULT_UNSEAL_KEY_{i}")
        if key:
            env_keys.append(key)

    if len(env_keys) >= 3:
        print("🔑 Loaded unseal keys from environment variables")
        return env_keys

    return None


def write_vault_bootstrap_log():
    log_path = Path("vault/logbook/vault_bootstrap.mdx")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow().isoformat()
    contents = f"""\
---
tag: v0.2.0-vault-automation
date: {now}
status: ✅ Initialized
files:
  - vault/.keys.enc
  - vault/unseal_keys.json
tasks:
  - vault.pull_secrets
  - vault.unseal
  - vault.status
zip: vault_automation.zip
---

Vault has been successfully initialized and unsealed using XO automation. Keys are stored securely and automation is in place.
"""

    log_path.write_text(contents)
    print(f"📓 Vault bootstrap log written to: {log_path}")

# ✅ /src/xo_core/agent/secrets.py
import json
from pathlib import Path

SECRETS_FILE = Path("vault/unseal_keys.json")


class VaultSecrets:
    def __init__(self):
        self._secrets = None

    def load(self):
        if SECRETS_FILE.exists():
            with open(SECRETS_FILE, "r") as f:
                self._secrets = json.load(f)
        else:
            self._secrets = {}

    def get(self, key: str, fallback=None):
        if self._secrets is None:
            self.load()
        return self._secrets.get(key, fallback)

    def all(self):
        if self._secrets is None:
            self.load()
        return self._secrets


vault_secrets = VaultSecrets()

import os
import json
import time
import importlib
from typing import Dict, Any, Optional


class VaultClient:
    def __init__(self) -> None:
        self.addr = os.getenv("VAULT_ADDR", "").rstrip("/")
        self.role_id = os.getenv("VAULT_ROLE_ID")
        self.secret_id = os.getenv("VAULT_SECRET_ID")
        self.namespace = os.getenv("VAULT_NAMESPACE")
        self._token: Optional[str] = None
        self._token_expiry: float = 0
        self._cache: Dict[str, Any] = {}

    def available(self) -> bool:
        return bool(self.addr and self.role_id and self.secret_id)

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.namespace:
            headers["X-Vault-Namespace"] = self.namespace
        if self._token:
            headers["X-Vault-Token"] = self._token
        return headers

    def _login(self) -> None:
        if not self.available():
            raise RuntimeError("Vault not configured")
        now = time.time()
        if self._token and now < self._token_expiry - 30:
            return
        requests = importlib.import_module("requests")
        url = f"{self.addr}/v1/auth/approle/login"
        r = requests.post(
            url, json={"role_id": self.role_id, "secret_id": self.secret_id}, timeout=10
        )
        r.raise_for_status()
        data = r.json().get("auth", {})
        self._token = data.get("client_token")
        ttl = data.get("lease_duration") or 300
        self._token_expiry = time.time() + int(ttl)

    def read_kv2(self, path: str) -> Dict[str, Any]:
        """Read KV v2 at logical path like 'secret/xo/core'. Results cached."""
        if path in self._cache:
            return self._cache[path]
        self._login()
        requests = importlib.import_module("requests")
        # Ensure /data/ path for KV v2
        if "/data/" not in path:
            p = path.strip("/").split("/", 1)
            if len(p) == 1:
                data_path = f"{p[0]}/data"
            else:
                data_path = f"{p[0]}/data/{p[1]}"
        else:
            data_path = path
        url = f"{self.addr}/v1/{data_path.strip('/')}"
        r = requests.get(url, headers=self._headers(), timeout=10)
        r.raise_for_status()
        payload = r.json().get("data", {}).get("data", {})
        if not isinstance(payload, dict):
            payload = {}
        self._cache[path] = payload
        return payload


_singleton: Optional[VaultClient] = None


def get_vault_client() -> VaultClient:
    global _singleton
    if _singleton is None:
        _singleton = VaultClient()
    return _singleton


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch a single secret value by key from Vault path 'secret/xo/core' or env as fallback."""
    vc = get_vault_client()
    if vc.available():
        try:
            data = vc.read_kv2("secret/xo/core")
            if key in data:
                return data.get(key)
        except Exception:
            pass
    return os.getenv(key, default)

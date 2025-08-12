from __future__ import annotations

import os
import json
import hashlib
from dataclasses import dataclass
from typing import Protocol, Dict, Any, Optional
import importlib


class SignerBackend(Protocol):
    name: str

    def sign_message(self, msg: bytes) -> Dict[str, Any]: ...

    def address(self) -> str: ...


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class DevFileSigner:
    name: str = "dev-file"
    key_path: str = os.path.expanduser(
        os.getenv("XO_SIGNER_FILE", "~/.config/xo-core/keys/dev.json")
    )

    def _load_privkey(self) -> bytes:
        p = os.path.expanduser(self.key_path)
        st = os.stat(p)
        # Require owner read/write only
        if (st.st_mode & 0o077) != 0:
            raise PermissionError("Key file must be 0600")
        with open(p, "r") as f:
            obj = json.load(f)
        # expect hex without 0x
        sk = bytes.fromhex(obj["private_key"].replace("0x", ""))
        if len(sk) != 32:
            raise ValueError("Invalid secp256k1 private key length")
        return sk

    def address(self) -> str:
        # lazy eth address derivation (no net): keccak(pubkey)[12:]
        Account = importlib.import_module("eth_account").Account  # dynamic import
        acct = Account.from_key(self._load_privkey())
        return acct.address

    def sign_message(self, msg: bytes) -> Dict[str, Any]:
        if len(msg) > 64 * 1024:
            raise ValueError("message too large")
        eth_account = importlib.import_module("eth_account")
        Account = eth_account.Account
        messages = eth_account.messages
        acct = Account.from_key(self._load_privkey())
        eth_msg = messages.encode_defunct(primitive=msg)
        sig = Account.sign_message(eth_msg, private_key=acct.key)
        sig_hex = sig.signature.hex()
        if not sig_hex.startswith("0x"):
            sig_hex = "0x" + sig_hex
        return {
            "algo": "secp256k1-eth_sign",
            "address": acct.address,
            "message_sha256": _sha256(msg),
            "signature": sig_hex,
            "v": int(sig.v),
            "r": hex(sig.r),
            "s": hex(sig.s),
        }


@dataclass
class VaultTransitSigner:
    name: str = "vault-transit"
    mount: str = os.getenv("XO_VAULT_MOUNT", "transit")
    key: str = os.getenv("XO_VAULT_KEY", "xo-signer")
    addr: str = os.getenv("VAULT_ADDR", "")
    role_id: Optional[str] = os.getenv("VAULT_ROLE_ID")
    secret_id: Optional[str] = os.getenv("VAULT_SECRET_ID")

    def _token(self) -> str:
        requests = importlib.import_module("requests")
        r = requests.post(
            f"{self.addr}/v1/auth/approle/login",
            json={"role_id": self.role_id, "secret_id": self.secret_id},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()["auth"]["client_token"]

    def address(self) -> str:
        # Optional: fetch from metadata or dedicated path; placeholder unknown
        return "vault:unknown"

    def sign_message(self, msg: bytes) -> Dict[str, Any]:
        base64_mod = importlib.import_module("base64")
        requests = importlib.import_module("requests")
        token = self._token()
        b64 = base64_mod.b64encode(msg).decode()
        url = f"{self.addr}/v1/{self.mount}/sign/{self.key}"
        r = requests.post(
            url,
            headers={"X-Vault-Token": token},
            json={"input": b64, "prehashed": False, "hash_algorithm": "sha2-256"},
            timeout=10,
        )
        r.raise_for_status()
        sig = r.json()["data"]["signature"]  # e.g., vault:v1:base64...
        return {
            "algo": "vault-transit-sha256",
            "address": self.address(),
            "message_sha256": hashlib.sha256(msg).hexdigest(),
            "signature": sig,
        }


def get_signer() -> SignerBackend:
    backend = os.getenv("XO_SIGNER_BACKEND", "dev-file").lower()
    if backend == "dev-file":
        return DevFileSigner()
    if backend == "vault-transit":
        return VaultTransitSigner()
    if backend == "defender":
        # placeholder: wire to relayer/defender later
        raise NotImplementedError("defender backend not implemented yet")
    raise ValueError(f"Unknown signer backend: {backend}")



import os
import requests

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
UNSEAL_KEYS = [
    os.getenv("VAULT_UNSEAL_KEY_1"),
    os.getenv("VAULT_UNSEAL_KEY_2"),
    os.getenv("VAULT_UNSEAL_KEY_3"),
]

def vault_unseal():
    for key in UNSEAL_KEYS:
        if not key:
            print("❌ Missing one or more VAULT_UNSEAL_KEYs in .envrc or environment.")
            return
        try:
            res = requests.put(
                f"{VAULT_ADDR}/v1/sys/unseal",
                json={"key": key}
            )
            res.raise_for_status()
            data = res.json()
            print(f"🔑 Unseal progress: {data.get('progress')}/3 (Sealed: {data.get('sealed')})")
            if data.get("sealed") is False:
                print("✅ Vault is now unsealed.")
                break
        except Exception as e:
            print(f"❌ Failed to unseal with provided key: {e}")
#!/usr/bin/env python3
"""
Rotate Vault Transit key and print the new version.
"""
import os, requests, sys

VAULT_ADDR = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = (
    os.environ.get("VAULT_TOKEN")
    or open(os.path.expanduser("~/.config/xo-vault/dev_token")).read().strip()
)
KEY = os.environ.get("XO_AUDIT_TRANSIT_KEY", "xo-audit")
r = requests.post(
    f"{VAULT_ADDR}/v1/transit/keys/{KEY}/rotate",
    headers={"X-Vault-Token": VAULT_TOKEN},
    timeout=20,
)
if r.status_code != 204:
    print("❌ rotate failed", r.status_code, r.text)
    sys.exit(1)
# read metadata to display latest version
m = requests.get(
    f"{VAULT_ADDR}/v1/transit/keys/{KEY}",
    headers={"X-Vault-Token": VAULT_TOKEN},
    timeout=20,
).json()
print(f"✅ rotated transit key '{KEY}' → latest_version={m['data']['latest_version']}")

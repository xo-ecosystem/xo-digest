"""
XO Vault Unseal Module - HashiCorp Vault integration for secrets management

This module provides:
- Vault unseal functionality with fallback key sources
- Client management with graceful error handling
- Integration with XO Vault API for secrets delegation
"""

import time
import requests
from pathlib import Path
import os
from .bootstrap import get_vault_client, get_vault_unseal_keys, write_vault_bootstrap_log

def vault_unseal():
    """Unseal HashiCorp Vault using keys from various sources with clear progress logging."""
    print("🔐 Starting HashiCorp Vault unseal process...")

    # Get unseal keys with fallback logic
    unseal_keys = get_vault_unseal_keys()
    if not unseal_keys:
        print("❌ No valid unseal method found. Please ensure one of:")
        print("   - vault/unseal_keys.json exists with valid keys")
        print("   - vault/.keys.enc exists with valid keys")
        print("   - VAULT_UNSEAL_KEY_1, VAULT_UNSEAL_KEY_2, VAULT_UNSEAL_KEY_3 environment variables")
        return False

    # Get vault client
    client = get_vault_client()
    if client is None:
        print("❌ Could not initialize vault client")
        return False

    # Check if vault is already unsealed
    try:
        if not client.sys.is_sealed():
            print("✅ HashiCorp Vault is already unsealed")
            return True
    except Exception as e:
        print(f"⚠️ Could not check vault status: {e}")
        # Continue with unseal attempt anyway

    # Unseal with progress tracking
    print(f"🔐 Attempting to unseal with {len(unseal_keys)} keys...")

    for i, key in enumerate(unseal_keys, 1):
        if not key:
            print(f"⚠️ Skipping empty key {i}")
            continue

        try:
            # Use hvac client if available, fallback to requests
            if hasattr(client, "sys") and hasattr(client.sys, "submit_unseal_key"):
                result = client.sys.submit_unseal_key(key)
                if result:
                    print(f"🔐 Unsealed key {i}/{len(unseal_keys)}")
                    if not client.sys.is_sealed():
                        print("✅ HashiCorp Vault unsealed successfully!")
                        write_vault_bootstrap_log()
                        return True
            else:
                # Fallback to direct HTTP requests
                vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
                res = requests.put(f"{vault_addr}/v1/sys/unseal", json={"key": key})
                res.raise_for_status()
                data = res.json()
                print(f"🔐 Unsealed key {i}/{len(unseal_keys)} - Progress: {data.get('progress')}/3")
                if data.get("sealed") is False:
                    print("✅ HashiCorp Vault unsealed successfully!")
                    write_vault_bootstrap_log()
                    return True

        except Exception as e:
            print(f"❌ Error unsealing with key {i}: {e}")

    print("❌ Failed to unseal HashiCorp Vault with provided keys")
    return False

def unseal_vault(c):
    """Fab task wrapper for vault unseal."""
    success = vault_unseal()
    if success:
        print("✅ HashiCorp Vault unseal task completed successfully")
    else:
        print("❌ HashiCorp Vault unseal task failed")
        exit(1)

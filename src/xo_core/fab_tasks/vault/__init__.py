"""
Vault module for XO Core.
"""

from invoke import Collection
import logging

# Create a local namespace for this module only
vault_ns = Collection("vault")

# Try to import chain namespace
try:
    from .chain import ns as chain_ns
    vault_ns.add_collection(chain_ns, name="auto")
except ImportError as e:
    logging.warning(f"⚠️ Chain namespace not loaded: {e}")

# Try to import sign_pulse namespace
try:
    from .sign_pulse import ns as sign_ns
    vault_ns.add_collection(sign_ns, name="sign")
except ImportError as e:
    logging.warning(f"⚠️ Sign pulse namespace not loaded: {e}")

# Try to import explorer sync
try:
    from .explorer import sync as explorer_sync
    vault_ns.add_task(explorer_sync, name="sync")
except ImportError as e:
    logging.warning(f"⚠️ Explorer sync not loaded: {e}")

# Export the namespace for external use
ns = vault_ns

__all__ = ["ns"]
"""
Canonical Vault package for XO.

This module intentionally avoids importing submodules at import time to
prevent circular imports during Fabric task discovery and test collection.
Import symbols directly from submodules, e.g.:

    from xo_core.vault.unseal import vault_unseal, vault_status
    from xo_core.vault.bootstrap import bootstrap_vault
"""

from importlib import import_module

__all__ = ["lazy", "require", "sign_all", "get_vault_client"]


def lazy(path: str):
    """Return a module loader; import happens on first attribute access."""
    module = None

    def _get():
        nonlocal module
        if module is None:
            module = import_module(path)
        return module

    return _get


def require(path: str):
    """Immediate import helper."""
    return import_module(path)


def sign_all(*args, **kwargs):
    """Passthrough to signing API without importing at module load time."""
    return require("xo_core.vault.api").sign_all(*args, **kwargs)  # type: ignore[attr-defined]


def get_vault_client(*args, **kwargs):
    """Passthrough to bootstrap.get_vault_client lazily."""
    return require("xo_core.vault.bootstrap").get_vault_client(*args, **kwargs)  # type: ignore[attr-defined]

# [o3-fix 2025-08-03] Lazy accessor to avoid circular imports
"""
XO Core Vault package

This initializer provides a lazy accessor `get_community_tasks` that defers
importing heavy sub-modules (`unseal`, `bootstrap`, `community_tasks`) until
they are actually needed.  This breaks the previous circular-import chain
triggered during module import time.
"""

from importlib import import_module
from typing import Any

__all__ = ["get_community_tasks"]


def get_community_tasks() -> Any:
    """Return the `xo_core.vault.community_tasks` module lazily.

    Doing the import at call-time avoids circular-import errors when
    `xo_core.vault` is imported by fab tasks at start-up.
    """
    return import_module("xo_core.vault.community_tasks")

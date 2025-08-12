"""
xo_core.vault
Lazy import facade to avoid circular imports between vault submodules.

No eager intra-package imports here. Use explicit submodule imports when needed.
Example:
    from xo_core.vault import unseal
    from xo_core.vault import pulse
"""

from importlib import import_module as _imp


def __getattr__(name: str):
    allowed = {
        "api",
        "chain",
        "community_tasks",
        "digest_gen",
        "explorer_index",
        "inbox_render",
        "ipfs_utils",
        "preview",
        "preview_generator",
        "pulse",
        "seals",
        "sign",
        "signing",
        "signal",
        "unseal",
    }
    if name in allowed:
        return _imp(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

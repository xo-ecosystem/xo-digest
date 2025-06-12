"""Unified Fabric task collection for xo‑core‑clean."""

from pathlib import Path
import sys
from invoke import Collection

# Resolve project root safely whether __file__ is defined or not (Fabric may exec this file twice)
if "__file__" in globals():
    PROJECT_ROOT = Path(__file__).resolve().parent
else:
    PROJECT_ROOT = Path.cwd()

# Ensure project root is on PYTHONPATH
sys.path.insert(0, str(PROJECT_ROOT))
# ------------------------------------------------------------------
# Cleanup: remove heavy objects so Invoke won't mis-treat them
# as config values during its second pass.
for _n in ("sys", "Path"):
    if _n in globals():
        del globals()[_n]
# ------------------------------------------------------------------

"""Unified Fabric task collection for xo‑core‑clean.

This file keeps a **single source of truth** for all task namespaces:
  • Pulse‑related tasks  →  fab_tasks.pulse_tasks
  • Vault‑related tasks  →  fab_tasks.vault_tasks
  • Optional agent work  →  xo_agent.tasks  (alias: xo)
  • Optional Agent0 work →  agent0.tasks    (alias: agent0)

A predictable hierarchy:
    fab -f fabfile.py --list
        pulse.*
        vault.*
        xo.*        (if present)
        agent0.*    (if present)

Root‑level convenience aliases:
    sync          →  pulse.sync
    archive-all   →  pulse.archive_all
"""

# ---------------------------------------------------------------------------
# Core task namespaces (required)
# ---------------------------------------------------------------------------
import fab_tasks.pulse_tasks as pulse_tasks
from fab_tasks import vault_tasks

ns = Collection()

# Add mandatory namespaces
ns.add_collection(Collection.from_module(pulse_tasks), name="pulse")
ns.add_collection(Collection.from_module(vault_tasks), name="vault")

# Convenience root‑level shortcuts
ns.add_task(pulse_tasks.sync, name="sync")
ns.add_task(pulse_tasks.archive_all, name="archive-all")

# ---------------------------------------------------------------------------
# Optional namespaces (don’t fail build if missing)
# ---------------------------------------------------------------------------
OPTIONAL_MODULES = [
    ("xo_agent.tasks", "xo"),
    ("agent0.tasks", "agent0"),
]

for module_path, alias in OPTIONAL_MODULES:
    try:
        mod = __import__(module_path, fromlist=["*"])
        ns.add_collection(Collection.from_module(mod), name=alias)
    except ImportError:
        # Gracefully skip missing optional modules
        print(f"⚠️  Optional tasks module not found: {module_path} (skipped)")

# ------------------------------------------------------------------
# Final cleanup so Invoke’s runtime config loader sees only picklable
# objects in the module namespace.
# ------------------------------------------------------------------
for _mod in ("pulse_tasks", "vault_tasks", "mod"):
    globals().pop(_mod, None)

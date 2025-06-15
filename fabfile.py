"""Unified Fabric task collection for xo‑core‑clean."""

import sys
from pathlib import Path
# src/xo_core/fabfile.py
from xo_core.fab_tasks.pulse_namespace import pulse_ns
# Add the src directory to the Python path
if "__file__" in globals():
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    sys.path.insert(0, str(Path(__file__).parent / "src" / "xo_core"))

from invoke import Collection

from xo_core.commitizen_tasks import cz_lint
from xo_core.fab_tasks import pulse_tasks, vault_tasks
from xo_core.fab_tasks.validate_tasks import validate_tasks

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

ns = Collection()

# Add mandatory namespaces
ns.add_collection(Collection.from_module(pulse_tasks), name="pulse")
ns.add_collection(Collection.from_module(vault_tasks), name="vault")

# Convenience root‑level shortcuts
ns.add_task(pulse_tasks.sync, name="sync")
ns.add_task(pulse_tasks.archive_all, name="archive-all")

# XO-Drop tasks
try:
    import xo_core.fab_tasks.drop_tasks as drop_tasks_mod

    ns.add_collection(Collection.from_module(drop_tasks_mod), name="drop")
    del drop_tasks_mod
except ImportError:
    print("⚠️  Optional tasks module not found: xo_core.fab_tasks.drop_tasks (skipped)")

# Register validate_tasks at root level
ns.add_task(validate_tasks, name="validate_tasks")

ns.add_task(cz_lint, name="cz-lint")
# ---------------------------------------------------------------------------
# Optional namespaces (don't fail build if missing)
# ---------------------------------------------------------------------------
OPTIONAL_MODULES = [
    ("xo_agent.tasks", "xo_agent"),
    ("xo_agent.tasks", "xo"),  # Alias for xo
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
# Final cleanup so Invoke's runtime config loader sees only picklable
# objects in the module namespace.
# ------------------------------------------------------------------
for _mod in ("pulse_tasks", "vault_tasks", "mod"):
    globals().pop(_mod, None)

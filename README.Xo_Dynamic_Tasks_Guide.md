# 📦 XO-Core Dynamic Task System Migration Guide

## ✅ Overview

This guide documents the migration from static Fabric task imports to a dynamic, modular loading system using `DynamicTaskLoader`. It outlines structure, rationale, and extensibility patterns for current and future XO-core automation.

---

## 🧠 Goals

* Eliminate unpicklable global objects (e.g., `drop_tasks = ...`) that crash Fabric runtime
* Modularize task loading to handle both required and optional namespaces
* Provide better dev DX via namespace docs, validation, and logging

---

## 📁 Key Files & Structure

```
xo-core/
├── fabfile.py                     # Entry point with clean, dynamic registration
├── src/xo_core/
│   ├── fab_tasks/
│   │   ├── dynamic_loader.py     # 🧠 DynamicTaskLoader class + config
│   │   ├── info_tasks.py         # ℹ️  Namespace + category doc/validate tasks
│   │   ├── pulse_tasks.py        # Pulse-related core tasks
│   │   ├── vault_tasks.py        # Vault automation tasks
│   │   └── drop_tasks.py         # (Optional, dynamically loaded)
│   ├── commitizen_tasks.py
│   └── ...
└── tests/
    └── test_dynamic_loader.py    # ✅ Unit tests for loader
```

---

## 🧩 How It Works

### 1. `fabfile.py`

```python
from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader
ns = DynamicTaskLoader().load_all()
```

### 2. `MODULE_CONFIGS`

```python
MODULE_CONFIGS = [
    {"path": "xo_core.fab_tasks.pulse_tasks", "name": "pulse", "required": True, "category": "core"},
    {"path": "xo_core.fab_tasks.drop_tasks", "name": "drop", "required": False, "category": "content"},
    {"path": "xo_agent.tasks", "name": "xo", "required": False, "category": "external"},
    ...
]
```

### 3. Runtime Cleanup

All dynamic imports are removed after task registration to prevent namespace pollution.

---

## 🚦 CLI Utilities

### Validate all modules:

```sh
fab namespace.validate-modules
```

### Print full tree:

```sh
fab --list
```

### Show docs by category:

```sh
fab namespace.list-categories
fab namespace.generate-docs
```

---

## 📜 Changelog Entry

```md
### Added
- `DynamicTaskLoader`: auto-imports Fabric task modules based on centralized config
- `info_tasks.py`: expose `namespace-info`, `generate-docs`, `validate-modules`
- Auto-generated `docs/task_namespaces.md` with all available namespaces

### Changed
- Refactored `fabfile.py` and `src/xo_core/fabfile.py` to remove all static task imports

### Fixed
- Resolved `UnpicklableConfigMember` errors due to static module usage in globals()
```

---

## ✨ Codex Scaffold Prompt

```md
Create a dynamic Fabric task loading system:
- Uses a `DynamicTaskLoader` class
- Reads a `MODULE_CONFIGS` list of dicts with `path`, `name`, `required`, and `category`
- Registers all task collections with Fabric
- Cleans up all dynamic imports from `globals()`
- Supports `validate-modules`, `namespace-info`, and `generate-docs` commands
- Optional: output a Markdown documentation file of available namespaces
```

---

## ✅ Next Steps

* [ ] Sync `docs/task_namespaces.md` to the Vault
* [ ] Share guide with core collaborators (e.g., Brie)
* [ ] Use this as the base for other subsystems (e.g., CI, archive, infra)

---

🔁 Reusable. Scalable. Battle-tested.
This pattern is ready to be adopted across all modular task loading needs in XO. 🚀


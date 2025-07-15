# fab_tasks/ — XO Task Automation

## Overview

This directory contains all automation tasks for the XO project, organized by namespace (vault, agent, seed, nft, pulse, tunnel, etc.). Each submodule exposes its own `Collection` for easy aggregation and extension.

## How Namespaces Work

- Each task file (e.g., `vault_tasks.py`, `agent_tasks.py`) defines a namespace using `invoke.Collection`.
- The master `Collection` in `fab_tasks/__init__.py` aggregates all submodule namespaces.
- The root `fabfile.py` exposes this master collection, so all tasks are available from the project root.

# XO fab_tasks Onboarding Guide

Welcome to the XO automation core!
This folder contains all Fabric tasks for automating and orchestrating XO's infrastructure, content, and agent flows.

## Structure

- **fab_tasks/**
  - `tunnel/` — tasks for managing tunnels (Cloudflare, local, etc)
  - `vault/` — tasks for secrets, signing, verification
  - `pulse/` — content and publishing automations
  - (add your own module here!)

## How to add a new task namespace

1. Create a subfolder or `.py` file inside `fab_tasks/`.
2. Export a namespace as `ns = Collection("your_namespace")` at the bottom.
3. In `fabfile.py`, add:
   ```python
   from fab_tasks.your_module import ns as your_ns
   namespace.add_collection(your_ns)
   ```
4. Test with:
   ```
   xo-fab your_namespace.your_task
   ```
5. Update this README as needed!

## Onboarding notes

- All optional imports (e.g. arweave, boto3) are wrapped so missing dependencies won't break the CLI.
- If a task fails due to a missing package, install it in your venv:
  ```
  pip install <package>
  ```
- Only clean up or remove legacy modules **after** confirming main flows work.

Welcome to XO — contribute, fork, and automate!

## Onboarding: Adding New Tasks/Namespaces

1. **Create your task file** in `fab_tasks/` (e.g., `my_tasks.py`).
2. **Define your tasks** using `@task` and group them in a `Collection` (e.g., `ns = Collection("my")`).
3. **Expose your collection** as `ns` at the bottom of your file.
4. **Edit `fab_tasks/__init__.py`** to import your module and add `ns` to the master collection:
   ```python
   from . import my_tasks
   ns.add_collection(my_tasks.ns, name="my")
   ```
5. **Test from root:** Run `invoke --list` to see your new namespace and tasks.

## Best Practices

- **Optional Dependencies:**
  - If your task requires an optional dependency (e.g., `arweave`), wrap the import in a `try/except ImportError` block and print a helpful message if missing. This prevents the CLI from breaking for users who don't need that feature.
  - Example:
    ```python
    try:
        from arweave import Wallet
    except ImportError:
        Wallet = None
        print("[WARN] arweave not installed. Vault signing will be disabled.")
    ```
- **Dependency Installation:**
  - Install required dependencies with pip:
    ```sh
    pip install arweave-python-client
    ```
- **Keep tasks modular:** Group related tasks in their own files and expose via `ns`.
- **Document your tasks:** Add docstrings and help messages for each task.

## Cleaning Up

- Only remove or refactor legacy/duplicate tasks after confirming all main flows work from the root.
- Use the `_incoming/` folder as a staging area for new modules/scripts before integration.

## Troubleshooting

- If a namespace or task is missing, check that it's imported and registered in `fab_tasks/__init__.py`.
- Use `invoke --list` to see all available tasks and namespaces.

---

Happy automating! 🎛️

# Fabric Tasks

This directory contains all Fabric task modules for the XO Core project, organized using a dynamic loading system that prevents `UnpicklableConfigMember` errors.

## 🚀 Dynamic Task Loader

The `dynamic_loader.py` module provides a robust, maintainable system for loading Fabric task modules without polluting the global namespace.

### Features

- **Safe Dynamic Loading**: All modules are loaded dynamically using `__import__()` to prevent static imports in global scope
- **Centralized Configuration**: Module metadata is defined in `MODULE_CONFIGS` with categories, descriptions, and requirements
- **Robust Error Handling**: Graceful handling of missing optional modules with detailed logging
- **Duplicate Detection**: Prevents duplicate collection names during registration
- **Module Validation**: Validates that loaded modules contain callable tasks
- **Comprehensive Logging**: Detailed logging with configurable verbosity
- **Future-Proof API**: Extensible design for adding new module categories and features

### Module Categories

- **Core**: Essential task modules (pulse, vault, summary, validation)
- **CI**: Continuous integration tasks (commitizen, linting)
- **Content**: Content management tasks (drops, publishing)
- **Runtime**: Runtime environment management
- **Testing**: Testing and diagnostics tasks
- **Info**: Information and documentation tasks
- **External**: External integrations (agents, third-party tools)

### Usage

#### Basic Usage

```python
from invoke import Collection
from xo_core.fab_tasks.dynamic_loader import load_all_modules

ns = Collection()
summary = load_all_modules(ns, verbose=True)
```

#### Custom Module Registration

```python
from xo_core.fab_tasks.dynamic_loader import register_modules, ModuleConfig

configs = [
    ModuleConfig(
        path="my.custom.tasks",
        name="custom_tasks",
        alias="custom",
        required=False,
        category="custom",
        description="Custom task module"
    )
]

summary = register_modules(ns, configs, verbose=True)
```

#### Adding New Modules

1. Create your task module in `fab_tasks/`
2. Add configuration to `MODULE_CONFIGS` in `dynamic_loader.py`:

```python
ModuleConfig(
    path="xo_core.fab_tasks.your_module",
    name="your_module",
    alias="your_alias",
    required=False,  # Set to True if required
    category="your_category",
    description="Description of your module"
)
```

### Information Tasks

The `info_tasks.py` module provides utilities for exploring and documenting the task system:

- `fab namespace.namespace-info`: Show detailed information about loaded namespaces
- `fab namespace.list-categories`: List all available task categories
- `fab namespace.generate-docs`: Generate markdown documentation
- `fab namespace.validate-modules`: Validate all module configurations

### Configuration Structure

Each module configuration includes:

- `path`: Full module import path
- `name`: Internal module name
- `alias`: Collection name in Fabric namespace (optional)
- `required`: Whether the module is required (default: False)
- `hidden`: Whether to skip loading (default: False)
- `category`: Module category for organization
- `description`: Human-readable description

### Error Handling

The loader handles various error scenarios:

- **Missing Required Modules**: Raises error and stops loading
- **Missing Optional Modules**: Logs warning and continues
- **Invalid Module Structure**: Logs error and marks as failed
- **Duplicate Collection Names**: Logs warning and skips duplicate
- **Import Errors**: Detailed error messages with context

### Logging

The loader provides comprehensive logging:

- **INFO**: Successful module loads and general information
- **WARNING**: Duplicate names, missing optional modules
- **ERROR**: Failed required modules, validation errors
- **DEBUG**: Detailed loading process (when verbose=True)

### Testing

Run the unit tests:

```bash
python -m unittest tests.test_dynamic_loader -v
```

### Migration from Static Imports

If you have existing static imports, replace them with dynamic loading:

**Before:**
```python
from xo_core.fab_tasks import some_tasks
ns.add_collection(Collection.from_module(some_tasks), name="some")
```

**After:**
```python
from xo_core.fab_tasks.dynamic_loader import load_required_module
load_required_module("xo_core.fab_tasks.some_tasks", "some", ns)
```

### Best Practices

1. **Always use dynamic loading** for task modules
2. **Provide meaningful descriptions** in module configurations
3. **Use appropriate categories** for organization
4. **Set required=True** only for essential modules
5. **Test module validation** before deployment
6. **Use verbose logging** during development
7. **Generate documentation** regularly with `fab namespace.generate-docs`

### Troubleshooting

#### UnpicklableConfigMember Error

If you encounter this error, check for:
- Static imports in `fabfile.py` or other config files
- Module references in global namespace
- Missing cleanup after dynamic imports

#### Module Not Found

For missing modules:
- Verify the module path in `MODULE_CONFIGS`
- Check if the module exists in the filesystem
- Ensure the module is in the Python path

#### Validation Errors

For validation failures:
- Ensure the module contains callable functions
- Check for proper `@task` decorators
- Verify module structure and imports

## 📁 Module Structure

```
fab_tasks/
├── __init__.py
├── dynamic_loader.py      # Main dynamic loading system
├── info_tasks.py          # Information and documentation tasks
├── pulse_tasks.py         # Pulse-related tasks
├── vault_tasks.py         # Vault-related tasks
├── summary_tasks.py       # Summary generation tasks
├── validate_tasks.py      # Validation utilities
├── drop_tasks.py          # Drop management tasks
├── runtime_tasks.py       # Runtime environment tasks
├── test_tasks.py          # Testing and diagnostics
└── ...                    # Other task modules
```

## 🔧 Development

### Adding New Task Modules

1. Create your task module with proper `@task` decorators
2. Add configuration to `MODULE_CONFIGS`
3. Test with `fab namespace.validate-modules`
4. Update documentation with `fab namespace.generate-docs`

### Extending the Loader

The `DynamicTaskLoader` class is designed for extensibility:

- Add new validation methods
- Implement caching mechanisms
- Add plugin support
- Create custom loading strategies

### Contributing

When contributing new task modules:

1. Follow the existing naming conventions
2. Add comprehensive docstrings
3. Include proper error handling
4. Add unit tests for new functionality
5. Update the module configuration
6. Generate updated documentation

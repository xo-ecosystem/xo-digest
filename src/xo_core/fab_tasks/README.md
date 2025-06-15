# fab_tasks/ — XO Task Automation

## Overview

This directory contains all automation tasks for the XO project, organized by namespace (vault, agent, seed, nft, pulse, tunnel, etc.). Each submodule exposes its own `Collection` for easy aggregation and extension.

## How Namespaces Work

- Each task file (e.g., `vault_tasks.py`, `agent_tasks.py`) defines a namespace using `invoke.Collection`.
- The master `Collection` in `fab_tasks/__init__.py` aggregates all submodule namespaces.
- The root `fabfile.py` exposes this master collection, so all tasks are available from the project root.

# XO fab_tasks Onboarding Guide

Welcome to the XO automation core!
This folder contains all Fabric tasks for automating and orchestrating XO’s infrastructure, content, and agent flows.

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

- All optional imports (e.g. arweave, boto3) are wrapped so missing dependencies won’t break the CLI.
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

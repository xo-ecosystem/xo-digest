# Task Namespaces

Details about task namespaces.

# Task Namespaces

XO Core organizes tasks into modular namespaces for clarity and maintainability.

## 🧭 Usage

- List all tasks:

  ```bash
  xo-fab --list
  ```

- Run a task in a namespace:
  ```bash
  xo-fab pulse.sync
  xo-fab vault.verify-all
  ```

## 📦 Available Namespaces

- `vault.` → Signing, snapshot, archive, and mesh tasks
- `pulse.` → Blog/post management
- `drop.` → XO drop deployment, syncing, previews
- `seal.` → Sealing and bundling tasks
- `env.` → Environment switching and status
- `storage.` → Storj-based asset handling
- `agent.` → Agent0-AI task coordination
- `backend.` → API health and orchestration
- `cosmos.` → Cross-service coordination and init

## 🔧 Create New Namespace

1. Add a new file under `src/xo_core/fab_tasks/<your_namespace>.py`
2. Use `@task` decorators and `Collection()` to register
3. Add to `fabfile.py` loader or dynamic imports

## 🧠 Tip

Namespace prefixes help separate responsibilities and scale across the XO ecosystem.

## 🧭 Onboarding Guide for New Devs (and Curious Explorers)

Whether you're jumping into XO Fabric automation for the first time or refining your own namespace:

### 💼 Getting Started

- Explore available namespaces:
  ```bash
  xo-fab --list
  ```
- Try out a common one:
  ```bash
  xo-fab pulse.sync
  ```

### 🧠 Authoring Your Own

- Add a new namespace file to:
  ```
  src/xo_core/fab_tasks/<your_namespace>.py
  ```
- Use the `@task` decorator from `invoke`.
- Register with a `Collection()` and plug it into `fabfile.py`.

### 💡 Pro Tips

- Modular tasks help scale across teams and services.
- Use `--debug` to trace issues.
- For errors like `No module named 'fab_tasks.xyz'`, check for missing `__init__.py`.

📚 All fabric usage is mirrored in Vault under:

```
/public/vault/daily/
```

## 📦 Vault Bundle Metadata

This file is included in the `core_docs_bundle` published to Vault.

Bundle Name: `core_docs_bundle`
Location: `/public/vault/daily/core_docs_bundle.zip`
Includes:

- `diagnose_cheatsheet.md`
- `task_namespaces.md`
- `env/envrc-switching.md`

Published via:

```bash
xo-fab pulse.sync:core_docs_bundle
xo-fab vault.bundle:core_docs_bundle
```

See full metadata in `core_docs_bundle.mdx` for reference and indexing.

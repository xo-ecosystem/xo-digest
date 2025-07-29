# Diagnose Cheatsheet

Troubleshooting tips and commands.

# Diagnose Cheatsheet

A quick reference for diagnosing and resolving issues in the XO Core environment.

## ✅ Setup & Environment

- Check if environment variables are loaded:
  ```bash
  direnv status
  env | grep XO_
  ```
- Reload `.envrc`:

  ```bash
  direnv reload
  ```

- Ensure Python environment is active:
  ```bash
  which python
  python --version
  ```

## 🔍 Debugging CLI & Tasks

- List available Fabric tasks:

  ```bash
  xo-fab --list
  ```

- Run a specific task with debug:

  ```bash
  python -m invoke -c fabfile <task> --debug
  ```

- Diagnose namespace load errors:
  ```bash
  python -m invoke -c fabfile diagnose.namespaces
  ```

## 🧪 FastAPI Health Check

- Check if API is running:

  ```bash
  curl -s http://localhost:8000/health | jq
  ```

- Access Swagger UI:
  http://localhost:8000/docs

## ⚠️ Common Issues

- ❌ `No module named '...fab_tasks'`:
  → Check `__init__.py` presence in `fab_tasks` subfolders.

- ❌ `direnv: .envrc is blocked`:
  → Run `direnv allow`.

- ❌ `fabfile.py` tasks not detected:
  → Ensure correct module structure and `invoke -c` is used.

## 💡 Tips

- Use `cursor .` or `code .` to launch the workspace.
- Keep `.vscode/extensions.json` updated for dev onboarding.
- Use `git status` to confirm sync before replacing files manually.

## 📚 Related

- See `docs/env/envrc-switching.md` for environment context switching.
- See `docs/task_namespaces.md` for organizing Fabric tasks.

## 🧭 Onboarding Guide for New Devs (and Curious Explorers)

Whether you're an experienced dev or someone like Brie jumping in with fresh eyes, here's how to start:

### 💼 Getting Started

- Launch the workspace:
  ```bash
  cursor .  # Or `code .` if using VS Code
  ```
- Recommended extensions will be suggested automatically. You can also check `.vscode/extensions.json` for manual install.
- Run this to view all available commands:
  ```bash
  xo-fab --list
  ```

### 🔁 Refreshing Files

If you've replaced or copied files into the workspace manually (via Finder/Explorer):

- In Cursor: use `Cmd+Shift+P → Reload Window` to refresh open tabs.
- If a file looks crossed out or stale, close and re-open it.

### 🧪 Health Check

- Ensure FastAPI backend is running:
  ```bash
  curl -s http://localhost:8000/health | jq
  ```
- Frontend is accessible via:
  ```
  http://localhost:5173/
  ```

### ✅ Verifying Fabric Tasks

- Run a test task:
  ```bash
  python -m invoke -c fabfile env.status
  ```
- Or check which ones are available:
  ```bash
  python -m invoke -c fabfile --list
  ```

💡 _Docs, diagnostics, and dev insights are all stored inside the Vault._ You can explore them later via:

```
/public/vault/daily/
```

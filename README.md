# 🔐 XO Agent – Vault Keeper

> Modular webhook + CLI agent system for the XO ecosystem, built to execute secure, lore-infused tasks across Pulse, Vault, DNS, Drops, and more.

---

## 🧠 About

The XO Agent is a FastAPI + CLI-powered task runner with GitHub webhook support. It listens to signed commands from CI or CLI, validates them with a shared secret, and executes corresponding Fabric-based tasks.

🌌 **Persona**: `Vault Keeper` — Guardian of the sealed drops and the living digital archive.

---

## 🚀 Features

- ✅ Modular **task registry** (YAML-based, dynamic)
- ✅ FastAPI server with `/agent/webhook`, `/agent/test`, `/agent/tasks`, etc.
- ✅ GitHub Actions → webhook integration
- ✅ Fabric task dispatching (e.g. `pulse.sync`, `vault.sign-all`)
- ✅ Secure `X-Agent-Secret` middleware
- ✅ Lore-preserving log messages
- ✅ Fly.io deploy-ready (`fly.toml`, `Dockerfile`)
- ✅ Developer-mode CLI (`run_agent.py`, `agent_cli.py`)

---

## 📦 Components

- **Pulse** — Immutable content and lore publishing
- **Vault** — Secure archival and signature layer
- **Drops** — NFT & asset bundles with living lore
- **DNS** — Domain automation and record sync
- **Agent** — Webhook + CLI task dispatcher

---

## 🧪 Test Locally

_Start the API in development mode:_

```bash
uvicorn xo_agents.api:app --port 8003 --reload
```

---

## 🔒 Secrets & Security Quickstart

**One-time setup**

```bash
# Move your local env files outside the repo and symlink back
make secure-move

# Commit only the index changes (once) to avoid pre-commit stash loops
git add .gitignore Makefile
git rm --cached -f .env .env.local env/.env env/.env.local 2>/dev/null || true
git commit -m "chore(secrets): untrack local env files and ignore" --no-verify

# Install hooks
pre-commit install --install-hooks
```

**Daily workflow**

- Edit your real secrets at: `~/.config/xo-core/env/.env.local`
  (symlinked at `env/.env.local` in the repo).
- Before pushing:
  ```bash
  make scan       # gitleaks + detect-secrets with excludes
  make prepush    # run all pre-commit hooks locally
  ```

**What `make scan` does**

- Runs **gitleaks** on the working tree.
- Runs **detect-secrets** across the repo with built-in excludes:
  - file excludes: `(^\.env|^env/\.env(\.local)?|\.png|\.jpg|\.jpeg|\.webp|\.pdf|\.zip|\.lock|\.md|\.yml|\.yaml)$`
  - line excludes: `secrets: inherit`

**Baseline guard in CI**

- PRs fail if `.secrets.baseline` changes unless the PR title or body includes **`[baseline-update]`**.
- Nightly CI runs both scanners; results upload as SARIF (for gitleaks).

**Common gotchas**

- If pre-commit "restores" a just-untracked file, it’s the stash/restore mechanism fixing another file in the same commit. Do the untracking in a **single, isolated commit** (see one-time setup above).
- If you truly need to refresh the baseline:
  ```bash
  detect-secrets scan \
    --all-files \
    --exclude-files '(^\.env|^env/\.env(\.local)?|\.png|\.jpg|\.jpeg|\.webp|\.pdf|\.zip|\.lock|\.md|\.yml|\.yaml)$' \
    --exclude-lines 'secrets: inherit' \
    > .secrets.baseline
  git add .secrets.baseline
  git commit -m "chore(security): refresh detect-secrets baseline [baseline-update]"
  ```

**Reminder**

- Never commit `.env`, `.env.local`, or `env/.env*`. The Makefile and ignore rules will keep them local-only.

---

## 🤝 Contributing

- Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and best practices.
- Run `make prepush` before submitting pull requests to ensure all checks pass.
- Remember to include **`[baseline-update]`** in your PR title or body if you update `.secrets.baseline`.

---

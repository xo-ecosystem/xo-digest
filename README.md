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

## 🧪 Test Locally

```bash
uvicorn xo_agents.api:app --port 8003 --reload
```

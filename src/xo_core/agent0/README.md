# xo-dev-scaffold

⚙️ XO development scaffold for rapid iteration across Vault, Agent0, and system watchdogs. Suitable for both local testing and containerized deployment.

## 🚀 Features

- 🐳 Docker Compose orchestration for Vault, Agent0 (Flask/Gunicorn), and optional local services
- 🔐 Multi-env configuration with `.env.*` patterns
- 👀 Health checks and autorecovery with `watchdog_agent.py`
- 🔁 Hot reload support for local development
- 📦 Lightweight, production-aware Gunicorn setup

## 📂 Scaffold Structure

- `docker-compose.yml` – main entrypoint for service orchestration
- `.env.template`, `.env.staging`, `.env.production` – environment presets
- `agent0/` – Flask+Gunicorn agent service (webui, transformers optional)
- `vault/` – FastAPI-based service for signing, secrets, and snapshots
- `watchdog_agent.py` – monitors container health and restarts crashed services

## 🛠️ Getting Started

```bash
docker-compose up --build
```

Or use:

```bash
./scripts/xo-dev-doctor.sh
```

to validate your setup.

---

## 🧠 Agent0 Dev Quickstart

This scaffold uses Agent0 as the core lightweight reasoning service.

### To get started with Agent0:

```bash
cd agent0
python app.py  # or use Gunicorn for production
```

### Optional setup:

- Install LLM weights or connect Ollama for local inference.
- Use the `webui/` folder to explore chat capabilities.
- `.agent-memory/` will store logs and reasoning traces (auto-ignored via .gitignore).

---

## 📡 Vault Signing API

The `vault/` folder provides a simple signing and verification API.

### Example:

```bash
curl -X POST http://localhost:8000/sign/your_slug
```

Or test via:

```bash
python vault/serve.py
```

Secrets are auto-loaded from `.env` and can be encrypted via Vault backend.

---

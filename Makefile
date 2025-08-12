#!/usr/bin/make -f

SHELL := /bin/bash
PORT ?= 8003

.PHONY: help lint test doctor vault-status vault-unseal vault-check agent-health secure detox version

help:
	@echo "🛠️  XO Core Makefile - Essential Tasks"
	@echo ""
	@echo "🔐 Vault:"
	@echo "  vault-status   Check Vault status"
	@echo "  vault-unseal   Unseal Vault with stored keys"
	@echo "  vault-check    Full Vault health check (non-blocking if unavailable)"
	@echo ""
	@echo "🤖 Agent:"
	@echo "  agent-health   Check agent system health"
	@echo ""
	@echo "⚙️  System:"
	@echo "  lint           Run lint (non-blocking)"
	@echo "  test           Run tests (non-blocking)"
	@echo "  doctor         Run combined checks (non-blocking)"
	@echo "  secure         Keep .env.local safe and ignored"
	@echo "  secure-move    Move env files to ~/.config and symlink back"
	@echo "  version        Show tool versions"
	@echo ""
	@echo "🛡️  Security:"
	@echo "  scan           Run local secret scans (gitleaks + detect-secrets with excludes)"
	@echo "  prepush        Run all pre-commit hooks"

lint:
	@echo "🔍 Running linting checks..."
	@python -m flake8 src/ --max-line-length=100 --ignore=E203,W503 || echo "⚠️  flake8 not installed or issues found (non-blocking)"

test:
	@echo "🧪 Running test suite..."
	@python -m pytest -q || echo "⚠️  Tests failed (non-blocking for doctor)"

doctor:
	@echo "🩺 Running XO Doctor Check..."
	@$(MAKE) lint || true
	@$(MAKE) test || true
	@$(MAKE) vault-check || echo "⚠️  vault-check skipped (xo-fab or script unavailable)"
	@$(MAKE) agent-health || true
	@echo "✅ Doctor completed (warnings above are non-blocking)."
	@echo "🔍 Validating .env.local presence..."
	@[ -f .env.local ] && echo "✅ .env.local found" || echo "⚠️  .env.local missing"
	@echo "🔍 Git hygiene..."
	@git status --porcelain | grep '^??' >/dev/null && echo '⚠️  Untracked files present' || echo '✅ No untracked files'
	@git diff --quiet || echo '⚠️  Uncommitted changes detected'

vault-status:
	@echo "🔍 Checking Vault status..."
	@python -c "import sys; sys.path.insert(0, 'src'); from xo_core.vault.bootstrap import get_vault_client; print('✅ Vault available' if get_vault_client() else '❌ Vault unavailable')"

vault-unseal:
	@echo "🔓 Unsealing Vault..."
	@python -c "import sys; sys.path.insert(0, 'src'); from xo_core.vault.unseal import vault_unseal; vault_unseal()"

vault-check:
	@echo "🩺 Running full Vault health check..."
	@export PYTHONPATH="$(PWD)/src" && xo-fab vault-check || echo "⚠️  xo-fab not available, skipping"

agent-health:
	@echo "🩺 Checking agent health..."
	@python scripts/agent_health_check.py || echo "⚠️  Agent health check script missing (non-blocking)"

secure:
	@echo "🔐 Ensuring env files are ignored and untracked..."
	@mkdir -p env
	@# Ensure ignore rules for all common env locations
	@for p in '.env' '.env.local' 'env/.env' 'env/.env.local'; do \
	  grep -qxF "$${p}" .gitignore || echo "$${p}" >> .gitignore; \
	done
	@# If any of these are already tracked, untrack them (but keep local copies)
	@for p in '.env' '.env.local' 'env/.env' 'env/.env.local'; do \
	  git ls-files --error-unmatch "$${p}" >/dev/null 2>&1 && git rm --cached -q "$${p}" || true; \
	done
	@# Tell git to leave local copies alone going forward
	@for p in '.env' '.env.local' 'env/.env' 'env/.env.local'; do \
	  git update-index --skip-worktree "$${p}" 2>/dev/null || true; \
	done
	@echo "✅ env files protected (ignored + untracked)."

# Default secret store outside the repo
SECRET_STORE ?= $(HOME)/.config/xo-core/env

# Move local env files outside the repo and symlink back
.PHONY: secure-move
secure-move:
	@echo "🔐 Moving env files to $(SECRET_STORE) and creating symlinks…"
	@mkdir -p $(SECRET_STORE) env
	# Move any present env files out of the repo (preserve existing ones)
	@[ -f .env ] && mv .env $(SECRET_STORE)/.env 2>/dev/null || true
	@[ -f .env.local ] && mv .env.local $(SECRET_STORE)/.env.local 2>/dev/null || true
	@[ -f env/.env ] && mv env/.env $(SECRET_STORE)/.env 2>/dev/null || true
	@[ -f env/.env.local ] && mv env/.env.local $(SECRET_STORE)/.env.local 2>/dev/null || true
	# Recreate symlink back into env/
	@[ -f $(SECRET_STORE)/.env.local ] && ln -snf $(SECRET_STORE)/.env.local env/.env.local || true
	@[ -f $(SECRET_STORE)/.env ] && ln -snf $(SECRET_STORE)/.env env/.env || true
	# Ensure ignore rules and untrack from git index
	@$(MAKE) secure
	@git rm --cached -f .env .env.local env/.env env/.env.local 2>/dev/null || true
	@git update-index --skip-worktree .env .env.local env/.env env/.env.local 2>/dev/null || true
	@echo "✅ Env files moved to $(SECRET_STORE) and symlinked (env/.env*, ignored & untracked)."

version:
	@echo "📦 XO Core"
	@echo "🐍 Python: $$(python --version 2>/dev/null || echo 'n/a')"
	@echo "📦 Fabric: $$(fab --version 2>/dev/null || echo 'n/a')"

# --- Security hardening tasks ---
.PHONY: bootstrap scan scan-history prepush

bootstrap:
	python -m pip install --upgrade pip || true
	pip install pre-commit detect-secrets || true
	pre-commit install || true

scan:
	@echo "🔎 Running gitleaks (working tree)…"
	@{ command -v gitleaks >/dev/null 2>&1 && gitleaks protect --config .gitleaks.toml --source . --redact --verbose; } || echo "gitleaks not installed; skipping"
	@echo "🔎 Running detect-secrets (repo, with excludes)…"
	@detect-secrets scan --all-files --exclude-files='(^\.env|^env/\.env(\.local)?|\.png|\.jpg|\.jpeg|\.webp|\.pdf|\.zip|\.lock|\.md|\.yml|\.yaml)$$' --exclude-lines='secrets: inherit' > .secrets.scan.json || true
	@detect-secrets audit --json .secrets.scan.json || true
	@rm -f .secrets.scan.json
	@echo "✅ scan complete"

scan-history:
	@echo "🕰️ Running gitleaks (full history)…"
	@{ command -v gitleaks >/dev/null 2>&1 && gitleaks detect --source . --redact --verbose --report-format sarif --report-path security-history.sarif; } || echo "gitleaks not installed; skipping"
	@echo "📄 SARIF report (if generated): security-history.sarif"

prepush:
	@pre-commit run --all-files

CONTEXT ?= manual

# --- Agent decode helpers ---
.PHONY: decode decode-file


decode:
	@PYTHONPATH="$(PWD)/src" fab agent.decode --input="$(INPUT)" --context="$(CONTEXT)" 2>/dev/null | jq . || \
	curl -s -H "X-Agent-Secret: $(XO_AGENT_SECRET)" -F "input=$(INPUT)" -F "context=$(CONTEXT)" "$(AGENT_URL)/agent/decode" | jq .

decode-file:
	@PYTHONPATH="$(PWD)/src" fab agent.decode --input="$(FILE)" --context=manual 2>/dev/null | jq . || \
	curl -s -H "X-Agent-Secret: $(XO_AGENT_SECRET)" -F "file=@$(FILE)" -F "context=manual" "$(AGENT_URL)/agent/decode" | jq .

.PHONY: open-decode
open-decode:
	@RUN_ID=$(RUN); if [ -z "$$RUN_ID" ]; then echo "Usage: make open-decode RUN=<run_id>"; exit 1; fi; \
	DIR="$(HOME)/.config/xo-core/decoded/$$RUN_ID"; \
	if [ -d "$$DIR" ]; then \
	  echo "Opening $$DIR"; \
	  open "$$DIR"; \
	  if [ -f "$$DIR/index.html" ]; then open "$$DIR/index.html"; fi; \
	else \
	  echo "Run directory not found: $$DIR"; exit 2; \
	fi

# --- Handle claim helpers ---
.PHONY: handle-claim handle-verify handle-activate handle-show

AGENT_URL ?= http://localhost:8003
XO_AGENT_SECRET ?=

handle-claim:
	@curl -s -X POST $(AGENT_URL)/agent/handles/claim \
	 -H "Content-Type: application/json" \
	 -H "X-Agent-Secret: $(XO_AGENT_SECRET)" \
	 -d '{"handle":"brie","method":"wallet"}' | jq .

handle-verify:
	@echo 'POST /agent/handles/verify with {"handle":"brie","signature":"<sig>"} or {"handle":"brie","token":"<token>"}'

handle-activate:
	@curl -s -X POST $(AGENT_URL)/agent/handles/activate \
	 -H "Content-Type: application/json" \
	 -H "X-Agent-Secret: $(XO_AGENT_SECRET)" \
	 -d '{"handle":"brie","display":"Brie"}' | jq .

handle-show:
	@PYTHONPATH="$(PWD)/src" fab handle.show --handle=brie | jq . 2>/dev/null || PYTHONPATH="$(PWD)/src" fab handle.show --handle=brie

.PHONY: kill-api-port
kill-api-port:
	@echo "🛑 Killing any process on port $(PORT)…"
	@PIDS=$$(lsof -ti :$(PORT) 2>/dev/null); \
	if [ -n "$$PIDS" ]; then \
	  echo "Found: $$PIDS"; \
	  kill -9 $$PIDS || true; \
	else \
	  echo "No process found on port $(PORT)"; \
	fi

# --- Serve API helpers ---
AGENT_URL ?= http://localhost:8003
XO_AGENT_SECRET ?=
.PHONY: serve-api open-api serve-api-prod

serve-api:
	@$(MAKE) kill-api-port
	@PYTHONPATH="$(PWD)/src" \
	XO_ALLOW_LEGACY_SECRET=1 \
	XO_CORS=$${XO_CORS:-http://localhost:5173} \
	XO_OIDC_ISSUER=$${XO_OIDC_ISSUER:-https://login.xo.center} \
	XO_OIDC_AUDIENCE=$${XO_OIDC_AUDIENCE:-api://xo-agent} \
	XO_OIDC_CLIENT_ID_SPA=$${XO_OIDC_CLIENT_ID_SPA:-xo-pulse-ui} \
	XO_OIDC_REDIRECT_URI=$${XO_OIDC_REDIRECT_URI:-http://localhost:8003/vault/ui} \
	XO_AGENT_SECRET=$${XO_AGENT_SECRET:-devsecret} \
	uvicorn xo_agents.api:app --port $(PORT) --reload

open-api:
	@python -c 'import webbrowser; webbrowser.open("http://localhost:8003/vault/ui")'

serve-api-prod:
	@$(MAKE) kill-api-port
	@PYTHONPATH="$(PWD)/src" \
	XO_OIDC_ISSUER=$${XO_OIDC_ISSUER:?set XO_OIDC_ISSUER} \
	XO_OIDC_AUDIENCE=$${XO_OIDC_AUDIENCE:?set XO_OIDC_AUDIENCE} \
	XO_OIDC_CLIENT_ID_SPA=$${XO_OIDC_CLIENT_ID_SPA:?set XO_OIDC_CLIENT_ID_SPA} \
	XO_OIDC_REDIRECT_URI=$${XO_OIDC_REDIRECT_URI:?set XO_OIDC_REDIRECT_URI} \
	XO_CORS=$${XO_CORS:-https://xo-pulse.com} \
	XO_AGENT_SECRET=$${XO_AGENT_SECRET:?set XO_AGENT_SECRET} \
	XO_API_RATELIMIT=1 uvicorn xo_agents.api:app --host 0.0.0.0 --port $(PORT) --log-level warning

# --- Sign helpers ---
.PHONY: sign-status sign-msg

sign-status:
	@PYTHONPATH="$(PWD)/src" fab sign.status || curl -s -H "X-Agent-Secret: $(XO_AGENT_SECRET)" "$(AGENT_URL)/agent/sign/status" | jq .

sign-msg:
	@PYTHONPATH="$(PWD)/src" fab sign.msg:'$(MESSAGE)' || curl -s -X POST \
	 -H "Content-Type: application/json" \
	 -H "X-Agent-Secret: $(XO_AGENT_SECRET)" \
	 -d '{"message":"$(MESSAGE)"}' \
	 "$(AGENT_URL)/agent/sign" | jq .

# --- Login proxy (Zitadel white-label) ---
LOGIN_APP ?= $(FLY_APP_NAME)
LOGIN_HOST ?= $(LOGIN_HOST)
ZITADEL_ISSUER ?= $(ZITADEL_ISSUER)
ALLOWED_ORIGINS ?= $(ALLOWED_ORIGINS)

.PHONY: login-proxy-deploy login-proxy-secrets login-proxy-run

login-proxy-deploy:
	@cd services/login-proxy && \
	sed -e 's|XO_APP_NAME_REPLACE|$(LOGIN_APP)|' \
	    -e 's|ZITADEL_ISSUER_REPLACE|$(ZITADEL_ISSUER)|' \
	    -e 's|LOGIN_HOST_REPLACE|$(LOGIN_HOST)|' \
	    -e 's|ALLOWED_ORIGINS_REPLACE|$(ALLOWED_ORIGINS)|' \
	    fly.toml > fly.generated.toml && \
	fly launch --copy-config --config fly.generated.toml --name $(LOGIN_APP) --now --region ams --yes

login-proxy-secrets:
	@echo "No secrets needed (PKCE). Ensure DNS CNAME $(LOGIN_HOST) → <app>.fly.dev hostname."

login-proxy-run:
	@cd services/login-proxy && uvicorn main:app --port 8080 --reload

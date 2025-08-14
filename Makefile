#!/usr/bin/make -f

SHELL := /bin/bash
PORT ?= 8003
APP ?= xo-vault

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

# --- SSE helpers ---
.PHONY: health redis-up sse-tail sse-broadcast

health:
	@curl -s localhost:8000/health | jq .
	@curl -s localhost:8000/health/redis | jq .

redis-up:
	@docker run --name xo-redis -p 6379:6379 -d redis:7 || true

sse-tail:
	@curl -N localhost:8000/message-bottle/stream

sse-broadcast:
	@REDIS_URL?=
	@if [ -z "$$MSG" ]; then echo 'Usage: make sse-broadcast MSG="hello" NAME="XO"'; exit 2; fi
	@NAME=$${NAME:-CLI} REDIS_URL=$$REDIS_URL python scripts/mb_broadcast.py -n "$$NAME" -m "$$MSG"

.PHONY: ops-post ops-get

ops-post:
	@if [ -z "$$OPS_BROADCAST_TOKEN" ]; then echo "Set OPS_BROADCAST_TOKEN"; exit 2; fi
	curl -s -X POST http://localhost:8000/ops/broadcast \
	  -H "Authorization: Bearer $$OPS_BROADCAST_TOKEN" \
	  -H "Content-Type: application/json" \
	  -d '{"type":"message_bottle.new","payload":{"name":"OPS","message":"hello from Makefile"}}' | jq .

ops-get:
	@if [ -z "$$OPS_BROADCAST_TOKEN" ]; then echo "Set OPS_BROADCAST_TOKEN"; exit 2; fi
	curl -s -G http://localhost:8000/ops/broadcast \
	  -H "X-OPS-Token: $$OPS_BROADCAST_TOKEN" \
	  --data-urlencode "name=OPS" \
	  --data-urlencode "message=hi via GET" | jq .

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

# --- Socials static build ---
.PHONY: socials-static
socials-static:
	@python3 scripts/render_socials_static.py

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

.PHONY: serve-api open-ui sign-url share-decode
serve-api:
	@XO_AGENT_SECRET=$${XO_AGENT_SECRET:-devsecret} XO_CORS=$${XO_CORS:-http://localhost:5173} PYTHONPATH=src uvicorn xo_agents.api:app --port 8003 --log-level info

open-ui:
	@open "$(AGENT_URL)/vault/ui" || true; open "$(AGENT_URL)/vault/ui/brie" || true

sign-url:
	@curl -s -H "X-Agent-Secret: $${XO_AGENT_SECRET:-devsecret}" \
		-H "Content-Type: application/json" \
		-d '{"run_id":"$(RUN)","ttl_s":$(or $(TTL),600)}' \
		"$(AGENT_URL)/agent/decode/sign-url" | jq .

share-decode:
	@URL=$$(make -s sign-url RUN=$(RUN) TTL=$(or $(TTL),600) | jq -r .url); \
	[ -n "$$URL" ] && open "$(AGENT_URL)$$URL"

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

# --- Simple dev helpers ---
.PHONY: setup lint format test precommit run dev

setup:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt
	if [ -f pyproject.toml ]; then pip install -e .; fi
	pre-commit install

lint:
	ruff check .

format:
	ruff format .

test:
	pytest -q

precommit:
	pre-commit run --all-files

run:
	uvicorn xo_core.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn xo_core.main:app --reload --host 0.0.0.0 --port 8000

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

# --- Storj S3 secrets helper ---------------------------------------------------
# Usage:
#   make storj-secrets APP=xo-vault [FILE=/path/to/Storj-S3-Credentials-*.txt]
#   make storj-secrets-show APP=xo-vault [FILE=/path/to/Storj-S3-Credentials-*.txt]
#
# Notes:
# - Provide FILE explicitly or the rule will pick the newest matching file in ~/Downloads/.
# - APP defaults to $(APP) (set globally above).

.PHONY: storj-secrets storj-secrets-show

storj-secrets:
	@APP_VAL="$(APP)"; \
	FILE_VAL="$(FILE)"; \
	if [ -z "$$FILE_VAL" ]; then \
	  FILE_VAL=$$(ls -t $$HOME/Downloads/Storj-S3-Credentials-*.txt 2>/dev/null | head -1); \
	fi; \
	if [ -z "$$FILE_VAL" ] || [ ! -f "$$FILE_VAL" ]; then \
	  echo "❌ No Storj credentials file found. Pass FILE=~/Downloads/Storj-S3-Credentials-*.txt"; \
	  exit 1; \
	fi; \
	echo "📄 Using $$FILE_VAL"; \
	ENDPOINT=$$(awk -F': ' '/^Endpoint/{print $$2}' "$$FILE_VAL"); \
	AKID=$$(awk -F': ' '/^Access Key ID/{print $$2}' "$$FILE_VAL"); \
	SAK=$$(awk -F': ' '/^Secret Access Key/{sub(/\r/,"");print $$2}' "$$FILE_VAL"); \
	BUCKET=$$(awk -F': ' '/^Bucket/{print $$2}' "$$FILE_VAL"); \
	if [ -n "$$ENDPOINT" ] && [ -n "$$AKID" ] && [ -n "$$SAK" ] && [ -n "$$BUCKET" ]; then \
	  fly secrets set \
	    XO_STORJ_S3_ENDPOINT="$$ENDPOINT" \
	    XO_STORJ_S3_BUCKET="$$BUCKET" \
	    XO_STORJ_S3_ACCESS_KEY_ID="$$AKID" \
	    XO_STORJ_S3_SECRET_ACCESS_KEY="$$SAK" \
	    -a "$$APP_VAL"; \
	else \
	  echo "❌ Failed to parse Storj credentials: $$FILE_VAL"; \
	  echo "   Expected lines: Endpoint, Access Key ID, Secret Access Key, Bucket"; \
	  exit 1; \
	fi

storj-secrets-show:
	@FILE_VAL="$(FILE)"; \
	if [ -z "$$FILE_VAL" ]; then \
	  FILE_VAL=$$(ls -t $$HOME/Downloads/Storj-S3-Credentials-*.txt 2>/dev/null | head -1); \
	fi; \
	if [ -z "$$FILE_VAL" ] || [ ! -f "$$FILE_VAL" ]; then \
	  echo "❌ No Storj credentials file found. Pass FILE=~/Downloads/Storj-S3-Credentials-*.txt"; \
	  exit 1; \
	fi; \
	echo "📄 Using $$FILE_VAL"; \
	awk 'BEGIN{print "---- Parsed Preview ----"} /^Endpoint|^Access Key ID|^Secret Access Key|^Bucket/{gsub(/\r/,"");print} END{print "------------------------"}' "$$FILE_VAL"

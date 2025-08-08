#!/usr/bin/make -f

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
	@echo "  version        Show tool versions"

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
	@echo "🔐 Ensuring .env.local is ignored and preserved..."
	@grep -qxF '.env.local' .gitignore || echo '.env.local' >> .gitignore
	@git update-index --assume-unchanged .env.local 2>/dev/null || true
	@git update-index --skip-worktree .env.local 2>/dev/null || true
	@echo "✅ .env.local protected."

version:
	@echo "📦 XO Core"
	@echo "🐍 Python: $$(python --version 2>/dev/null || echo 'n/a')"
	@echo "📦 Fabric: $$(fab --version 2>/dev/null || echo 'n/a')"
"""
xo_core.vault
Lazy import facade to avoid circular imports between vault submodules
when tests/tasks import from xo_core.vault.* during collection.

Do NOT perform any eager intra-package imports at module import time.
"""

from typing import Any

__all__ = [
    # modules exposed lazily
    "unseal",
    "bootstrap",
    "api",
    "utils",
    # function passthroughs commonly imported from package root
    "sign_all",
    "get_vault_client",
]

def __getattr__(name: str) -> Any:
    if name == "unseal":
        from . import unseal as m
        return m
    if name == "bootstrap":
        from . import bootstrap as m
        return m
    if name == "api":
        from . import api as m
        return m
    if name == "utils":
        from . import utils as m
        return m
    raise AttributeError(f"module 'xo_core.vault' has no attribute {name!r}")

def sign_all(*args, **kwargs):
    # Defer to implementation in .api (or update if moved)
    from .api import sign_all as _sign_all  # type: ignore
    return _sign_all(*args, **kwargs)

def get_vault_client(*args, **kwargs):
    # Defer to implementation in .bootstrap (or update if moved)
    from .bootstrap import get_vault_client as _get_vault_client  # type: ignore
    return _get_vault_client(*args, **kwargs)
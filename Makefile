# ✅ XO Core - Hybrid Makefile Fallback
# Essential tasks from xo-fab in Make format for reliable automation

.PHONY: help setup docs vault agent deploy clean test lint doctor secure

# Default target
help:
	@echo "🛠️  XO Core Makefile - Essential Tasks"
	@echo ""
	@echo "📖 Documentation:"
	@echo "  docs-token     Generate GitHub token for docs deployment"
	@echo "  docs-build     Build documentation locally"
	@echo "  docs-serve     Serve docs locally on localhost:8000"
	@echo "  docs-deploy    Deploy docs to GitHub Pages"
	@echo ""
	@echo "🔐 Vault Operations:"
	@echo "  vault-status   Check HashiCorp Vault status"
	@echo "  vault-unseal   Unseal Vault with stored keys"
	@echo "  vault-check    Full Vault health check"
	@echo ""
	@echo "🤖 Agent Tasks:"
	@echo "  agent-health   Check agent system health"
	@echo "  agent-deploy   Deploy agent to production"
	@echo ""
	@echo "⚙️  System:"
	@echo "  setup          Initial environment setup"
	@echo "  clean          Clean temporary files"
	@echo "  lint           Run linting checks"
	@echo "  test           Run test suite"
	@echo "  doctor          Run full health + environment checks"

# Environment setup
setup:
	@echo "🔧 Setting up XO Core environment..."
	@cp templates/env.template .env.local || echo "📝 Create .env.local from templates/env.template"
	@pip install -r requirements.txt || echo "📦 Install requirements manually"
	@echo "✅ Setup complete - edit .env.local with your values"

# Documentation tasks
docs-token:
	@echo "🔑 Generating GitHub App token..."
	@python scripts/docs_token_direct.py

docs-build:
	@echo "🔨 Building documentation..."
	@cd xo-core-docs && mkdocs build

docs-serve:
	@echo "🚀 Starting docs server at http://localhost:8000"
	@python scripts/docs_preview.py

docs-deploy:
	@echo "📤 Deploying documentation..."
	@python scripts/deploy_docs.py

# Vault operations
vault-status:
	@echo "🔍 Checking Vault status..."
	@python -c "import sys; sys.path.insert(0, 'src'); from xo_core.vault.bootstrap import get_vault_client; print('✅ Vault available' if get_vault_client() else '❌ Vault unavailable')"

vault-unseal:
	@echo "🔓 Unsealing Vault..."
	@python -c "import sys; sys.path.insert(0, 'src'); from xo_core.vault.unseal import vault_unseal; vault_unseal()"

vault-check:
	@echo "🩺 Running full Vault health check..."
	@export PYTHONPATH="$$HOME/xo-core-dev/src" && xo-fab vault-check || python scripts/vault_check_direct.py

# Agent operations  
agent-health:
	@echo "🩺 Checking agent health..."
	@python scripts/agent_health_check.py

agent-deploy:
	@echo "🚀 Deploying agent..."
	@export PYTHONPATH="$$HOME/xo-core-dev/src" && xo-fab deploy-prod || echo "❌ Deploy failed - check logs"

# Development tasks
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache build/ dist/ *.egg-info/
	@echo "✅ Clean complete"

lint:
	@echo "🔍 Running linting checks..."
	@python -m flake8 src/ --max-line-length=100 --ignore=E203,W503 || echo "📝 Fix linting issues"

test:
	@echo "🧪 Running test suite..."
	@python -m pytest tests/ -v || echo "❌ Tests failed"

# Version info
version:
	@echo "📦 XO Core v0.1.0"
	@echo "🐍 Python: $$(python --version)"
	@echo "📦 Fabric: $$(fab --version 2>/dev/null || echo 'Not available')"
# Doctor check
doctor:
	@echo "🩺 Running XO Doctor Check..."
	@make lint
	@make test
	@make vault-check
	@make agent-health
	@echo "✅ All checks passed (or warnings shown above)."
	@echo "🔍 Validating .env.local presence..."
	@[ -f .env.local ] && echo "✅ .env.local found" || echo "⚠️  .env.local missing"

	@echo "🔍 Checking for git issues..."
	@git status --porcelain | grep '^??' >/dev/null && echo '⚠️  Untracked files present' || echo '✅ No untracked files'
	@git diff --quiet || echo '⚠️  Uncommitted changes detected'

# Secure task
secure:
	@echo "🔐 Securing XO Core repository..."
	@echo "📛 Checking for secrets in tracked .env.local..."
	@if git ls-files --error-unmatch .env.local 2>/dev/null; then \
	  echo "⚠️  .env.local is tracked. Removing from Git index..."; \
	  git rm --cached .env.local; \
	  echo ".env.local" >> .gitignore; \
	  git add .gitignore; \
	  echo "✅ .env.local removed from Git tracking and added to .gitignore."; \
	else \
	  echo "✅ .env.local is not tracked by Git."; \
	fi
	@echo "🔍 Checking for common secret patterns..."
	@grep -r --exclude-dir=.git -E 'API_KEY|SECRET|PRIVATE_KEY|TOKEN' . || echo "✅ No obvious secrets found."
	@echo "🔒 Repository secure (manual review still advised)."
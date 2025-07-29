.PHONY: help dev test publish flush fab

help:
	@echo "Available commands:"
	@echo "  make dev       - Start local dev env"
	@echo "  make test      - Run all tests"
	@echo "  make publish   - Sync or deploy project"
	@echo "  make prepare-commit - Run black, isort, pyupgrade before committing"

dev: flush
	@echo "🔧 Starting dev mode..."
	@npm run dev

test:
	@echo "🧪 Running tests..."
	@python -m unittest discover tests/

publish:
	@echo "🚀 Publishing or syncing..."
	@xo-cli publish

lint:
	@echo "🔍 Running pre-commit hooks..."
	@pre-commit run --all-files

typecheck:
	@echo "🧠 Running mypy type checks..."
	@mypy .

validate:
	@echo "✅ Validating all Fabric task modules..."
	@xo-fab doctor --verbose || echo '⚠️ Task validation failed.'

ci:
	@echo "✅ Running full CI suite (lint + test + typecheck + validate)..."
	@make lint && make test && make typecheck && make validate

doctor:
	@echo "🩺 Running code cleanup and format checks..."
	pre-commit run --all-files || echo '⚠️ Pre-commit issues detected'

release:
	@tox -e cz || (echo "❌ Tests failed. Aborting release."; exit 1)

test-html:
	@mkdir -p reports
	@ts=$$(date +%Y%m%d_%H%M%S); \
	pytest tests/ --html=reports/test_report_$$ts.html --self-contained-html && \
	open reports/test_report_$$ts.html

test-vault:
	pytest tests/test_vault.py

# TODO: Add more commands
# Run formatters before committing
prepare-commit:
	@echo "🔄 Running formatters before staging..."
	pre-commit run black --all-files
	pre-commit run isort --all-files
	pre-commit run pyupgrade --all-files

patch-bundle:
	@echo "📦 Bundling .patch and task summary..."
	@mkdir -p patch_bundle
	@git diff > patch_bundle/changes.patch
	@fab patch.bundle --output-dir=patch_bundle --include-logs
	@echo "✅ Patch bundle created in patch_bundle/"

cosmic-align:
	@echo "🌌 Running XO Core Cosmic Alignment..."
	@fab cosmic-align

cosmic-align-dry:
	@echo "🌌 Running XO Core Cosmic Alignment (Dry Run)..."
	@fab cosmic-align --dry-run

dns-check:
	@echo "🌐 Checking DNS configuration..."
	@fab dns.check --validate-resolution

dns-check-dry:
	@echo "🌐 Checking DNS configuration (Dry Run)..."
	@fab dns.check --dry-run --validate-resolution

deploy-test:
	@echo "🧪 Testing all service deployments..."
	@fab deploy.all

deploy-test-dry:
	@echo "🧪 Testing all service deployments (Dry Run)..."
	@fab deploy.all --dry-run

health-check:
	@echo "🏥 Running health checks for all services..."
	@fab deploy.health --service=vault
	@fab deploy.health --service=inbox
	@fab deploy.health --service=preview
	@fab deploy.health --service=agent0

patch-review:
	@echo "🩹 Launching local patch review UI..."
	@make patch-bundle
	@python scripts/serve_patch_review.py & sleep 2 && open http://localhost:8000

install:
	@echo "📦 Installing main dependencies..."
	@pip install -r requirements.txt

install-dev:
	@echo "🛠️ Installing dev dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt || true

pulse-dev:
	@echo "⚙️ Running pulse.dev sequence..."
	@xo-fab pulse.dev

test-loader:
	@echo "🔍 Testing dynamic task loader..."
	@python scripts/test_loader.py

# Pulse tasks
pulse-new:
	@echo "🆕 Creating a new pulse..."
	@xo-fab pulse.new --slug=test_pulse

pulse-sign:
	@echo "✍️ Signing pulse..."
	@xo-fab pulse.sign --slug=test_pulse

pulse-sync:
	@echo "🔄 Syncing pulse..."
	@xo-fab pulse.sync --slug=test_pulse

pulse-publish:
	@echo "📢 Publishing pulse..."
	@xo-fab pulse.publish --slug=test_pulse

pulse-review:
	@echo "🧪 Reviewing pulse output..."
	@xo-fab pulse.review --slug=test_pulse --dry-run

# Flush caches: Python __pycache__, .pyc, mypy and pytest caches
flush:
	@echo "🧼 Flushing Python caches..."
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache
	@echo "✅ Cache flush complete."

# Run xo-fab after flushing caches
fab: flush
	@xo-fab
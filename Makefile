.PHONY: help dev test publish

help:
	@echo "Available commands:"
	@echo "  make dev       - Start local dev env"
	@echo "  make test      - Run all tests"
	@echo "  make publish   - Sync or deploy project"
	@echo "  make prepare-commit - Run black, isort, pyupgrade before committing"

dev:
	@echo "🔧 Starting dev mode..."
	@xo-cli dev

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
	@xo-fab validate-tasks || echo '⚠️ Task validation failed.'

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
	@xo-fab summary.to-md --save-to=patch_bundle/task_summary_$(shell date +%F).md || true
	@cp task_summary*.md patch_bundle/ 2>/dev/null || true

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
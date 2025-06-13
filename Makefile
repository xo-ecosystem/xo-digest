.PHONY: help dev test publish

help:
	@echo "Available commands:"
	@echo "  make dev       - Start local dev env"
	@echo "  make test      - Run all tests"
	@echo "  make publish   - Sync or deploy project"

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

ci:
	@echo "✅ Running full CI suite (lint + test + typecheck)..."
	@make lint && make test && make typecheck

release:
	@tox -e cz || (echo "❌ Tests failed. Aborting release."; exit 1)
# TODO: Add more commands
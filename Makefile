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

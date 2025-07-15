#!/bin/bash

echo "🔒 Cleaning up dev scratch and cache dirs..."

TARGETS=(
  ".direnv"
  ".history"
  ".cursor"
  ".wrangler/tmp"
  "__pycache__"
)

# Walk through node_modules/ and remove nested /tmp/
find . -type d -path "*/node_modules/tmp" -prune -exec rm -rf {} +

# Clean top-level matches
for target in "${TARGETS[@]}"; do
  find . -type d -name "$target" -prune -exec rm -rf {} +
done

echo "✅ Cleanup complete."

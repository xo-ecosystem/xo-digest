#!/usr/bin/env bash
set -euo pipefail

echo "Running preflight secret scan…"
BLOCK_PATTERNS=(
  "-----BEGIN .* PRIVATE KEY-----"
  "AKIA[0-9A-Z]{16}"
  "xox[baprs]-[0-9a-zA-Z-]{10,48}"
  "ghp_[0-9A-Za-z]{36}"
  "A3T[A-Z0-9]{16}"
)

git diff --cached -U0 | sed -n 's/^+//p' > /tmp/_staged.txt || true

for rx in "${BLOCK_PATTERNS[@]}"; do
  if grep -E -q "$rx" /tmp/_staged.txt; then
    echo "❌ Potential secret detected matching: $rx"
    exit 1
  fi
done

echo "✅ Preflight OK"

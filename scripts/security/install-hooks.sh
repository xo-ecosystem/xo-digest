#!/usr/bin/env bash
set -euo pipefail

mkdir -p .git/hooks
ln -sf ../../scripts/security/preflight.sh .git/hooks/pre-push
chmod +x scripts/security/preflight.sh .git/hooks/pre-push
echo "✅ Pre-push hook installed"

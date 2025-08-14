#!/usr/bin/env bash
# Source ETH envs and run sweep once
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$REPO_ROOT/scripts/xoenv.sh" eth >/dev/null
set -a; source /tmp/xo-env.sh; set +a
cd "$REPO_ROOT"
npm run --silent sweep

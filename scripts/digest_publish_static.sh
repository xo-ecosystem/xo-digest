#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/digest"
TARGET="$ROOT/xo-digest/site"

node "$ROOT/scripts/digest_build_static.js"

mkdir -p "$TARGET"
cp "$OUT/index.html" "$TARGET/index.html"

git -C "$ROOT/xo-digest" add site/index.html
git -C "$ROOT/xo-digest" commit -m "Digest: update static site" || true
git -C "$ROOT/xo-digest" push origin "$(git -C "$ROOT/xo-digest" branch --show-current)"
echo "Pushed digest site to xo-digest/site/index.html"

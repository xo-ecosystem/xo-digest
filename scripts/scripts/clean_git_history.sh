#!/bin/bash

set -e

echo "🔁 Cloning xo-core into xo-core-mirror.git..."
git clone --mirror xo-core xo-core-mirror.git

cd xo-core-mirror.git
echo "🧹 Filtering out venv folders..."
git filter-repo --path-glob '*/venv/*' --invert-paths

cd ..
echo "🗑 Removing old xo-core..."
rm -rf xo-core

echo "📦 Restoring from clean mirror..."
git clone xo-core-mirror.git xo-core

echo "✅ Done! xo-core is now history-clean, venv-free, and safe."

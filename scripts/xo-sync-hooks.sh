#!/bin/bash
set -e
echo '🔁 Syncing XO core config files to target repos...'

echo '📁 Syncing to /home/sandbox/xo-dev-scaffold'
cp /home/sandbox/xo-core/.gitignore /home/sandbox/xo-dev-scaffold/.gitignore || true
cp /home/sandbox/xo-core/.pre-commit-config.yaml /home/sandbox/xo-dev-scaffold/.pre-commit-config.yaml || true
cp /home/sandbox/xo-core/.envrc /home/sandbox/xo-dev-scaffold/.envrc || true
mkdir -p /home/sandbox/xo-dev-scaffold/vault/daily
touch /home/sandbox/xo-dev-scaffold/vault/daily/.gitkeep
cd /home/sandbox/xo-dev-scaffold && pre-commit install && pre-commit clean

echo '📁 Syncing to /home/sandbox/xo-digest'
cp /home/sandbox/xo-core/.gitignore /home/sandbox/xo-digest/.gitignore || true
cp /home/sandbox/xo-core/.pre-commit-config.yaml /home/sandbox/xo-digest/.pre-commit-config.yaml || true
cp /home/sandbox/xo-core/.envrc /home/sandbox/xo-digest/.envrc || true
mkdir -p /home/sandbox/xo-digest/vault/daily
touch /home/sandbox/xo-digest/vault/daily/.gitkeep
cd /home/sandbox/xo-digest && pre-commit install && pre-commit clean

echo '📁 Syncing to /home/sandbox/xo-doll-factory'
cp /home/sandbox/xo-core/.gitignore /home/sandbox/xo-doll-factory/.gitignore || true
cp /home/sandbox/xo-core/.pre-commit-config.yaml /home/sandbox/xo-doll-factory/.pre-commit-config.yaml || true
cp /home/sandbox/xo-core/.envrc /home/sandbox/xo-doll-factory/.envrc || true
mkdir -p /home/sandbox/xo-doll-factory/vault/daily
touch /home/sandbox/xo-doll-factory/vault/daily/.gitkeep
cd /home/sandbox/xo-doll-factory && pre-commit install && pre-commit clean
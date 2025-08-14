#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VAULT_ADDR="http://127.0.0.1:8200"
CONFIG_DIR="$HOME/.config/xo-vault"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$HOME/Library/Logs"
mkdir -p "$CONFIG_DIR" "$LAUNCHD_DIR" "$LOG_DIR" /run/secrets/xo || true

echo "🔧 Installing Vault (Homebrew)…"
if ! command -v vault >/dev/null 2>&1; then
  brew install vault
fi

# Symlink plists to launchd
ln -sf "$REPO_ROOT/config/launchd/com.xo.vault.plist" "$LAUNCHD_DIR/com.xo.vault.plist"
ln -sf "$REPO_ROOT/config/launchd/com.xo.vault-agent.plist" "$LAUNCHD_DIR/com.xo.vault-agent.plist"

echo "🚀 Starting Vault server via launchd…"
launchctl unload "$LAUNCHD_DIR/com.xo.vault.plist" >/dev/null 2>&1 || true
launchctl load -w "$LAUNCHD_DIR/com.xo.vault.plist"

export VAULT_ADDR="$VAULT_ADDR"

# Ensure Vault storage dir exists (Homebrew on Apple Silicon)
mkdir -p /opt/homebrew/var/vault || true

# Wait for Vault socket
for i in {1..30}; do
  nc -z 127.0.0.1 8200 && break || sleep 1
done

# Initialize/unseal on first run
if ! vault status >/dev/null 2>&1; then
  echo "🔐 Initializing Vault (one-time)…"
  vault operator init -key-shares=1 -key-threshold=1 > "$CONFIG_DIR/init.out"
fi

UNSEAL_KEY="$(grep 'Unseal Key 1:' "$CONFIG_DIR/init.out" | awk '{print $4}')"
ROOT_TOKEN="$(grep 'Initial Root Token:' "$CONFIG_DIR/init.out" | awk '{print $4}')"

echo "🔓 Unsealing Vault…"
vault operator unseal "$UNSEAL_KEY" >/dev/null

echo "🔑 Logging in as root (local dev)…"
export VAULT_TOKEN="$ROOT_TOKEN"
vault login "$ROOT_TOKEN" >/dev/null

# Enable KV v2 and store default bucket name (empty keys for now)
if ! vault secrets list | grep -q '^kv/'; then
  echo "📦 Enabling KV v2 at kv/"
  vault secrets enable -path=kv kv-v2 >/dev/null
fi

echo "📝 Writing placeholder secret kv/xo/storj (you will overwrite with real keys)…"
vault kv put kv/xo/storj \
  S3_ACCESS_KEY_ID="REPLACE_ME" \
  S3_SECRET_ACCESS_KEY="REPLACE_ME" \  # pragma: allowlist secret
  S3_ENDPOINT="https://gateway.storjshare.io" \
  S3_BUCKET="xo-vault-sealed" >/dev/null

# Policy allowing agent to read only the Storj secret
cat > "$CONFIG_DIR/xo-storj-read.hcl" <<'HCL'
path "kv/data/xo/storj" { capabilities = ["read"] }
HCL
vault policy write xo-storj-read "$CONFIG_DIR/xo-storj-read.hcl" >/dev/null

# AppRole for agent
if ! vault auth list | grep -q approle; then
  vault auth enable approle >/dev/null
fi

vault write auth/approle/role/xo-agent \
  token_policies="xo-storj-read" \
  token_ttl=24h token_max_ttl=72h >/dev/null

vault read -field=role_id auth/approle/role/xo-agent/role-id > "$CONFIG_DIR/role_id"
vault write -field=secret_id -f auth/approle/role/xo-agent/secret-id > "$CONFIG_DIR/secret_id"

# Ensure template config paths exist in agent.hcl (already pointing to $HOME/.config/xo-vault)
# Start/Reload Vault Agent
echo "🤖 Starting Vault Agent via launchd…"
launchctl unload "$LAUNCHD_DIR/com.xo.vault-agent.plist" >/dev/null 2>&1 || true
launchctl load -w "$LAUNCHD_DIR/com.xo.vault-agent.plist"

# Wait for first render
for i in {1..20}; do
  [[ -s /tmp/xo-env.sh ]] && [[ -s /run/secrets/xo/storj.json ]] && break || sleep 1
done

echo "✅ Bootstrap complete."
echo "➡  Next steps:"
echo "   1) Put your real Storj S3 keys into Vault:"
echo "      vault login $ROOT_TOKEN"
printf '%s\n' \
  "      vault kv put kv/xo/storj \\" \
  "         S3_ACCESS_KEY_ID=<your_access_key> \\" \
  "         S3_SECRET_ACCESS_KEY=<your_secret_key> \\" \
  "         S3_ENDPOINT=https://gateway.storjshare.io \\" \
  "         S3_BUCKET=xo-vault-sealed"
echo "   2) Load envs in any shell when needed:  set -a; source /tmp/xo-env.sh; set +a"
echo "   3) Or read JSON directly from:          /run/secrets/xo/storj.json"

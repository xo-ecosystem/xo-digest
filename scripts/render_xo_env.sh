#!/usr/bin/env bash
set -euo pipefail
export VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-$(awk '/Initial Root Token:/ {print $4}' ~/.config/xo-vault/init.out)}"
[ -n "${VAULT_TOKEN:-}" ] || { echo "❌ No VAULT_TOKEN available"; exit 1; }

json=$(curl -sS -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/kv/data/xo/storj")
ak=$(jq -r '.data.data.S3_ACCESS_KEY_ID'     <<<"$json")
sk=$(jq -r '.data.data.S3_SECRET_ACCESS_KEY' <<<"$json")
ep=$(jq -r '.data.data.S3_ENDPOINT'          <<<"$json")
bk=$(jq -r '.data.data.S3_BUCKET'            <<<"$json")

[ "$ak" != "null" ] && [ -n "$ak" ] || { echo "❌ Missing S3_ACCESS_KEY_ID"; exit 1; }
[ "$sk" != "null" ] && [ -n "$sk" ] || { echo "❌ Missing S3_SECRET_ACCESS_KEY"; exit 1; }
[ "$ep" != "null" ] && [ -n "$ep" ] || { echo "❌ Missing S3_ENDPOINT"; exit 1; }
[ "$bk" != "null" ] && [ -n "$bk" ] || { echo "❌ Missing S3_BUCKET"; exit 1; }

cat > /tmp/xo-env.sh <<EOF
export XO_STORJ_S3_ACCESS_KEY_ID="$ak"
export XO_STORJ_S3_SECRET_ACCESS_KEY="$sk"
export XO_STORJ_S3_ENDPOINT="$ep"
export XO_STORJ_S3_BUCKET="$bk"
export AWS_ACCESS_KEY_ID="$ak"
export AWS_SECRET_ACCESS_KEY="$sk"
export AWS_S3_ENDPOINT="$ep"
export S3_BUCKET="$bk"
EOF
echo "✅ wrote /tmp/xo-env.sh"
#!/usr/bin/env bash
set -euo pipefail
export VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"

# Prefer current shell token; otherwise use the bootstrap root token file
VAULT_TOKEN="${VAULT_TOKEN:-$(awk '/Initial Root Token:/ {print $4}' ~/.config/xo-vault/init.out)}"
[ -n "$VAULT_TOKEN" ] || { echo "❌ No VAULT_TOKEN available"; exit 1; }

json=$(curl -sS -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/kv/data/xo/storj")

# Extract fields
ak=$(jq -r '.data.data.S3_ACCESS_KEY_ID'     <<<"$json")
sk=$(jq -r '.data.data.S3_SECRET_ACCESS_KEY' <<<"$json")
ep=$(jq -r '.data.data.S3_ENDPOINT'          <<<"$json")
bk=$(jq -r '.data.data.S3_BUCKET'            <<<"$json")

# Validate
[ "$ak" != "null" ] && [ -n "$ak" ] || { echo "❌ Missing S3_ACCESS_KEY_ID in Vault"; exit 1; }
[ "$sk" != "null" ] && [ -n "$sk" ] || { echo "❌ Missing S3_SECRET_ACCESS_KEY in Vault"; exit 1; }
[ "$ep" != "null" ] && [ -n "$ep" ] || { echo "❌ Missing S3_ENDPOINT in Vault"; exit 1; }
[ "$bk" != "null" ] && [ -n "$bk" ] || { echo "❌ Missing S3_BUCKET in Vault"; exit 1; }

cat > /tmp/xo-env.sh <<EOF
export XO_STORJ_S3_ACCESS_KEY_ID="$ak"
export XO_STORJ_S3_SECRET_ACCESS_KEY="$sk"
export XO_STORJ_S3_ENDPOINT="$ep"
export XO_STORJ_S3_BUCKET="$bk"
# Optional aliases for tools that expect AWS_* names:
export AWS_ACCESS_KEY_ID="$ak"
export AWS_SECRET_ACCESS_KEY="$sk"
export AWS_S3_ENDPOINT="$ep"
export S3_BUCKET="$bk"
EOF

echo "✅ Wrote /tmp/xo-env.sh (bucket=$bk, endpoint=$ep)"

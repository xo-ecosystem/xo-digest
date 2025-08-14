#!/usr/bin/env bash
# XO env switcher: storj | pinata | eth | wallet | all
set -euo pipefail
profile="${1:-all}"
export VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-$(awk '/Initial Root Token:/ {print $4}' ~/.config/xo-vault/init.out)}"
jq() { command jq "$@"; } 2>/dev/null
fetch() { curl -sS -H "X-Vault-Token: $VAULT_TOKEN" "$VAULT_ADDR/v1/$1"; }
acc="# generated: $(date -u +%FT%TZ)\nexport XO_ENV_PROFILE=\"$profile\""

if [[ "$profile" == "storj" || "$profile" == "all" ]]; then
  js=$(fetch kv/data/xo/storj)
  ak=$(jq -r '.data.data.S3_ACCESS_KEY_ID'     <<<"$js")
  sk=$(jq -r '.data.data.S3_SECRET_ACCESS_KEY' <<<"$js")
  ep=$(jq -r '.data.data.S3_ENDPOINT'          <<<"$js")
  bk=$(jq -r '.data.data.S3_BUCKET'            <<<"$js")
  acc+=$'\n'"export XO_STORJ_S3_ACCESS_KEY_ID=\"$ak\""
  acc+=$'\n'"export XO_STORJ_S3_SECRET_ACCESS_KEY=\"$sk\""
  acc+=$'\n'"export XO_STORJ_S3_ENDPOINT=\"$ep\""
  acc+=$'\n'"export XO_STORJ_S3_BUCKET=\"$bk\""
  acc+=$'\n'"export AWS_ACCESS_KEY_ID=\"$ak\""
  acc+=$'\n'"export AWS_SECRET_ACCESS_KEY=\"$sk\""
  acc+=$'\n'"export AWS_S3_ENDPOINT=\"$ep\""
  acc+=$'\n'"export S3_BUCKET=\"$bk\""
fi

if [[ "$profile" == "pinata" || "$profile" == "all" ]]; then
  js=$(fetch kv/data/xo/pinata)
  jwt=$(jq -r '.data.data.PINATA_JWT'          <<<"$js")
  gw=$(jq -r  '.data.data.PINATA_GATEWAY_BASE' <<<"$js")
  k=$(jq -r   '.data.data.PINATA_API_KEY // empty'    <<<"$js")
  s=$(jq -r   '.data.data.PINATA_API_SECRET // empty' <<<"$js")
  acc+=$'\n'"export PINATA_JWT=\"$jwt\""
  acc+=$'\n'"export PINATA_GATEWAY_BASE=\"$gw\""
  [[ -n "$k" ]] && acc+=$'\n'"export PINATA_API_KEY=\"$k\""
  [[ -n "$s" ]] && acc+=$'\n'"export PINATA_API_SECRET=\"$s\""
fi

if [[ "$profile" == "eth" || "$profile" == "all" ]]; then
  js=$(fetch kv/data/xo/eth)
  if [[ $(jq -r '.data|type' <<<"$js") != "null" ]]; then
    rpc=$(jq -r '.data.data.RPC_URL'     <<<"$js")
    cid=$(jq -r '.data.data.CHAIN_ID'    <<<"$js")
    cold=$(jq -r '.data.data.COLD_ADDRESS' <<<"$js")
    thresh=$(jq -r '.data.data.SWEEP_THRESHOLD_ETH // "0.25"' <<<"$js")
    acc+=$'\n'"export XO_ETH_RPC_URL=\"$rpc\""
    acc+=$'\n'"export XO_ETH_CHAIN_ID=\"$cid\""
    acc+=$'\n'"export XO_ETH_COLD_ADDRESS=\"$cold\""
    acc+=$'\n'"export XO_ETH_SWEEP_THRESHOLD_ETH=\"$thresh\""
  fi
fi

if [[ "$profile" == "wallet" || "$profile" == "all" ]]; then
  # Hot wallet kept OUT of /tmp by default. Export only if XO_LOAD_WALLET_KEY=1.
  js=$(fetch kv/data/xo/wallets/hot) || js=""
  if [[ -n "$js" && $(jq -r '.data|type' <<<"$js") != "null" ]]; then
    addr=$(jq -r '.data.data.ADDRESS' <<<"$js")
    acc+=$'\n'"export XO_WALLET_ADDRESS=\"$addr\""
    if [[ "${XO_LOAD_WALLET_KEY:-0}" = "1" ]]; then
      pkb64=$(jq -r '.data.data.PRIVATE_KEY_B64' <<<"$js")
      pk=$(echo -n "$pkb64" | base64 -d)
      acc+=$'\n'"export XO_WALLET_PRIVATE_KEY=\"$pk\""
    fi
  fi
fi

echo -e "$acc" > /tmp/xo-env.sh
echo "✅ wrote /tmp/xo-env.sh for profile=$profile"

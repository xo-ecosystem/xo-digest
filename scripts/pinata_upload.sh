#!/usr/bin/env bash
# Upload a file (or stdin) to Pinata using PINATA_JWT; prints CID
set -euo pipefail
TMP=""
cleanup(){ [[ -n "$TMP" && -f "$TMP" ]] && rm -f "$TMP"; }
trap cleanup EXIT

FILE="${1:-}"
[[ -n "${PINATA_JWT:-}" ]] || { echo "❌ PINATA_JWT not set (load via scripts/xoenv.sh pinata)"; exit 1; }
if [[ -z "$FILE" || "$FILE" == "-" ]]; then
  TMP=$(mktemp)
  cat - > "$TMP"
  FILE="$TMP"
fi

[[ -f "$FILE" ]] || { echo "❌ file not found: $FILE"; exit 1; }

resp=$(curl -sS -X POST \
  -H "Authorization: Bearer $PINATA_JWT" \
  -F file=@"$FILE" \
  https://api.pinata.cloud/pinning/pinFileToIPFS)

cid=$(echo "$resp" | jq -r '.IpfsHash // .cid // empty')
[[ -n "$cid" ]] || { echo "❌ upload failed: $resp"; exit 1; }
echo "$cid"

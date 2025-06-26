#!/bin/bash
# upload_to_arweave.sh
# This script uploads .yml files to Arweave and logs the results with timestamps.

set -e

SIGNED_DIR="./xo-drops/drops/eighth_seal"
[ -d "$SIGNED_DIR" ] || SIGNED_DIR="./xo-drops-local-backup/drops/eighth_seal"
VAULT_LOG="./vault/logs/arweave_uploads.log"
ARWEAVE_WALLET="./secrets/arweave.json"

for file in "$SIGNED_DIR"/*.yml; do
  echo "📤 Uploading $file to Arweave..."

  TX_ID=$(python3 - <<EOF
import arweave
import json

wallet = arweave.Wallet("${ARWEAVE_WALLET}")
tx = arweave.Transaction(wallet, data=open("${file}", "rb").read())
tx.add_tag("App-Name", "XO-Drop")
tx.sign()
tx.send()
print(tx.id)
EOF
)

  echo "$file: $TX_ID" >> "$VAULT_LOG"
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $file → $TX_ID" >> "$VAULT_LOG"
  echo "✅ Uploaded: $file → $TX_ID"
done

echo "🗂️ All files processed and logged in $VAULT_LOG"
#!/usr/bin/env bash
set -euo pipefail

# Config
SOURCE_DIR="${VAULT_BACKUP_SOURCE:-/data}"
S3_ENDPOINT="${XO_STORJ_S3_ENDPOINT:-}"
S3_BUCKET="${XO_STORJ_S3_BUCKET:-}"
AWS_ACCESS_KEY_ID="${XO_STORJ_S3_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${XO_STORJ_S3_SECRET_ACCESS_KEY:-}"
AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
PREFIX="${BACKUP_PREFIX:-$(date +%F)/$(date +%H%M%S)}"

export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION

if [[ -z "$S3_ENDPOINT" || -z "$S3_BUCKET" || -z "$AWS_ACCESS_KEY_ID" || -z "$AWS_SECRET_ACCESS_KEY" ]]; then
  echo "[backup] Missing Storj S3 configuration; skipping." >&2
  exit 0
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "[backup] Source dir '$SOURCE_DIR' not found; skipping." >&2
  exit 0
fi

mkdir -p /tmp/backup
ARCHIVE="/tmp/backup/vault-$(date +%Y%m%d-%H%M%S).tar.gz"
HASHFILE="${ARCHIVE}.sha256"

echo "[backup] Creating archive from $SOURCE_DIR …"
tar -C "$SOURCE_DIR" -czf "$ARCHIVE" .
sha256sum "$ARCHIVE" | awk '{print $1}' > "$HASHFILE"

S3_BASE="s3://${S3_BUCKET}/${PREFIX}"
echo "[backup] Uploading to ${S3_BASE} …"
aws s3 cp --endpoint-url "$S3_ENDPOINT" "$ARCHIVE" "${S3_BASE}/$(basename "$ARCHIVE")"
aws s3 cp --endpoint-url "$S3_ENDPOINT" "$HASHFILE" "${S3_BASE}/$(basename "$HASHFILE")"

echo "[backup] Done."

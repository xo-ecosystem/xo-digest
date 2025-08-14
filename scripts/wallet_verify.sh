#!/usr/bin/env bash
set -euo pipefail

# Verify (and optionally sign) an EVM hash/signature pair.
# Modes:
#   1) Legacy positional:
#        wallet_verify.sh <0x32_byte_hash> <signature|->
#   2) Flagged:
#        wallet_verify.sh --hash <0xhash> [--sign] [--account xo-hot] [--json]
#        wallet_verify.sh --hash-file <path> [--keccak] [--sign] [--account xo-hot] [--json]
#
# Notes:
#   - --sign uses wallet_sign.sh with --recover by default (Touch ID Keychain flow)
#   - If signature is '-', it is read from stdin
#   - --hash-file uses SHA-256 unless --keccak is specified

usage() {
  cat >&2 <<USAGE
Usage:
  # legacy positional
  $0 <0x32_byte_hash> <signature|->

  # flagged
  $0 --hash <0x32_byte_hash> [--sign] [--account xo-hot] [--json]
  $0 --hash-file <path> [--keccak] [--sign] [--account xo-hot] [--json]
USAGE
  exit 1
}

hash_is_valid() {
  [[ "$1" =~ ^0x[0-9a-fA-F]{64}$ ]]
}

sig_is_valid() {
  [[ "$1" =~ ^0x[0-9a-fA-F]{130}$ ]]
}

HASH=""
SIG_IN=""
ACCOUNT="xo-hot"
WANT_JSON="0"
WANT_SIGN="0"
HASH_FILE=""
USE_KECCAK="0"

if [[ "${1:-}" == "--hash" || "${1:-}" == "--hash-file" || "${1:-}" == "--help" ]]; then
  # New flagged interface
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --hash)
        HASH="${2:-}"; shift 2;;
      --hash-file)
        HASH_FILE="${2:-}"; shift 2;;
      --keccak)
        USE_KECCAK="1"; shift;;
      --sign)
        WANT_SIGN="1"; shift;;
      --account)
        ACCOUNT="${2:-}"; shift 2;;
      --json)
        WANT_JSON="1"; shift;;
      --help|-h)
        usage;;
      *)
        echo "Unknown option: $1" >&2; usage;;
    esac
  done

  if [[ -n "$HASH_FILE" ]]; then
    [[ -f "$HASH_FILE" ]] || { echo "❌ File not found: $HASH_FILE" >&2; exit 1; }
    if [[ "$USE_KECCAK" == "1" ]]; then
      # Keccak-256 of file via Node + ethers
      HASH="$(node --input-type=module -e '
        import fs from "fs";
        import { keccak256 } from "ethers";
        const buf = fs.readFileSync(process.argv[1]);
        // ethers keccak256 expects hex string or BytesLike; Buffer is fine
        console.log(keccak256(buf));
      ' "$HASH_FILE")"
    else
      # SHA-256 of file (shasum portable)
      HASH="0x$(shasum -a 256 "$HASH_FILE" | awk '{print $1}')"
    fi
  fi

  hash_is_valid "$HASH" || { echo "❌ Invalid or missing --hash (need 0x + 64 hex)" >&2; usage; }

  if [[ "$WANT_SIGN" == "1" ]]; then
    # Sign first (recover included by default)
    if [[ "$WANT_JSON" == "1" ]] && command -v jq >/dev/null 2>&1; then
      JSON="$(./scripts/wallet_sign.sh "$HASH" "$ACCOUNT" --json --recover)"
      SIG_IN="$(printf '%s' "$JSON" | jq -r .serialized)"
      SIGNER_ADDR="$(printf '%s' "$JSON" | jq -r .address)"
    else
      # Text fallback
      OUT="$(./scripts/wallet_sign.sh "$HASH" "$ACCOUNT" --recover)"
      SIG_IN="$(printf '%s\n' "$OUT" | sed -n '1p')"
      SIGNER_ADDR="$(printf '%s\n' "$OUT" | awk -F= '/^addr=/{print $2}' || true)"
    fi
  fi

  # If not signing, expect user to provide signature via stdin or separate call;
  # but in flagged form without --sign we only verify if SIG_IN is given via stdin:
  if [[ -z "$SIG_IN" && ! -t 0 ]]; then
    SIG_IN="$(cat - | tr -d '\r\n')"
  fi
  [[ -n "$SIG_IN" ]] || { echo "❌ No signature provided (use --sign or pipe one to stdin)." >&2; exit 1; }

else
  # Legacy positional
  HASH="${1:-}"
  SIG_IN="${2:-}"
  hash_is_valid "$HASH" || usage
  if [[ "$SIG_IN" == "-" ]]; then
    SIG_IN="$(cat - | tr -d '\r\n')"
  fi
fi

SIG="$(printf '%s' "$SIG_IN" | tr -d '\r\n')"
sig_is_valid "$SIG" || { echo "❌ Invalid signature format. Expect 0x + 130 hex (65-byte serialized sig)." >&2; exit 1; }

# Recover with ethers
ADDR="$(env HASH="$HASH" SIG="$SIG" node --input-type=module -e '
  import { recoverAddress, Signature } from "ethers";
  const hash = process.env.HASH;
  const sig  = process.env.SIG;
  if (!hash || !sig) { process.exit(2); }
  console.log(recoverAddress(hash, Signature.from(sig)));
')"

if [[ "$WANT_JSON" == "1" ]]; then
  # Compose JSON (prefer signer addr if we signed; else recovered)
  if [[ -n "${SIGNER_ADDR:-}" ]]; then
    printf '{\n  "hash": "%s",\n  "signature": "%s",\n  "recovered_address": "%s",\n  "signer_address": "%s"\n}\n' "$HASH" "$SIG" "$ADDR" "$SIGNER_ADDR"
  else
    printf '{\n  "hash": "%s",\n  "signature": "%s",\n  "recovered_address": "%s"\n}\n' "$HASH" "$SIG" "$ADDR"
  fi
else
  echo "$ADDR"
fi

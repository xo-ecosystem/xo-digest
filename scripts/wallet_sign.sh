#!/usr/bin/env bash
# Sign a 0x-prefixed 32-byte hash using EVM privkey from macOS Keychain (or XO_WALLET_PRIVATE_KEY)
# - Fetches from Keychain via wallet_store_keychain.sh if XO_WALLET_PRIVATE_KEY not set
# - Normalizes key to 0x + 64 hex
# - Prints serialized signature AND r/s/v components
# - Flags:
#     --json    : output JSON {serialized,r,s,v,address?}
#     --recover : also print recovered address (text mode prints addr=..., JSON adds "address")
set -euo pipefail

HASH="${1:-}"
ACCOUNT="${2:-xo-hot}"
MODE="text"
RECOVER="0"

# Parse optional flags in $3 and $4 (simple)
for opt in "${3:-}" "${4:-}"; do
  case "$opt" in
    --json|json) MODE="json" ;;
    --recover)   RECOVER="1" ;;
    "" ) ;;
    *) ;; # ignore unknown
  esac
done

if [[ ! "$HASH" =~ ^0x[0-9a-fA-F]{64}$ ]]; then
  echo "Usage: $0 <0x32_byte_hash> [account] [--json] [--recover]" >&2
  echo "       hash must be 0x + 64 hex chars (keccak256/sha256 digest)" >&2
  exit 1
fi

# 1) Obtain private key (Keychain if env not set)
if [[ -n "${XO_WALLET_PRIVATE_KEY:-}" ]]; then
  PK="$XO_WALLET_PRIVATE_KEY"
else
  PK="$("$(dirname "$0")/wallet_store_keychain.sh" get "$ACCOUNT" | tr -d '\r\n')"
fi

# 2) Normalize to 0x + 64 hex
PK_HEX="${PK#0x}"
PK_HEX="${PK_HEX//$'\n'/}"   # strip stray newlines just in case
PK_HEX="${PK_HEX//$'\r'/}"
if [[ ! "$PK_HEX" =~ ^[0-9a-fA-F]{64}$ ]]; then
  echo "❌ Invalid or missing private key (expected 64 hex chars, with or without 0x)." >&2
  echo "   • Store via: ./scripts/wallet_store_keychain.sh put $ACCOUNT 0xYOUR_PRIVKEY_HEX" >&2
  exit 1
fi
PK_NORM="0x$PK_HEX"

# 3) Sign with ethers v6 and print serialized + r/s/v (and optional recovered address)
env PK="$PK_NORM" HASH="$HASH" MODE="$MODE" RECOVER="$RECOVER" node --input-type=module -e '
  import { SigningKey, getBytes, Signature, recoverAddress } from "ethers";
  const pk      = process.env.PK;
  const hash    = process.env.HASH;
  const mode    = (process.env.MODE || "text").toLowerCase();
  const recover = process.env.RECOVER === "1";
  if (!pk)  { console.error("Missing PK in env");  process.exit(1); }
  if (!hash){ console.error("Missing HASH in env");process.exit(1); }

  const sigObj = Signature.from(new SigningKey(pk).sign(getBytes(hash)));
  const addr   = recover ? recoverAddress(hash, sigObj) : null;

  if (mode === "json" || mode === "--json") {
    const out = { serialized: sigObj.serialized, r: sigObj.r, s: sigObj.s, v: sigObj.v };
    if (addr) out.address = addr;
    console.log(JSON.stringify(out, null, 2));
  } else {
    console.log(sigObj.serialized);
    console.log(`r=${sigObj.r}`);
    console.log(`s=${sigObj.s}`);
    console.log(`v=${sigObj.v}`);
    if (addr) console.log(`addr=${addr}`);
  }
'

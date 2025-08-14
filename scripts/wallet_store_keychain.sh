#!/usr/bin/env bash
# Store/retrieve EVM hot key in macOS Keychain (Touch ID prompts enabled in Keychain Access).
set -euo pipefail

CMD="${1:-help}"
SERVICE="XO_HOT_EVM_PRIVKEY"
ACCOUNT="${2:-xo-hot}"

trim_all() {
  # remove spaces, tabs, CR/LF
  printf '%s' "$1" | tr -d '\r\n\t '
}

strip_0x() {
  local key="$1"
  echo "${key#0x}"
}

add_0x() {
  local key="$1"
  [[ "$key" == 0x* ]] && echo "$key" || echo "0x${key}"
}

case "$CMD" in
  put)
    KEY_HEX_RAW="${3:-}"
    [[ -n "$KEY_HEX_RAW" ]] || { echo "Usage: $0 put <account> <privkey>"; exit 1; }
    KEY_HEX=$(strip_0x "$(trim_all "$KEY_HEX_RAW")")
    # validate exact 64 hex chars
    if [[ ! "$KEY_HEX" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ invalid private key: need 64 hex chars (with or without 0x)" >&2
      exit 1
    fi
    security add-generic-password -a "$ACCOUNT" -s "$SERVICE" -w "$KEY_HEX" -U >/dev/null
    echo "✅ stored in keychain ($SERVICE/$ACCOUNT, without 0x)"
    ;;
  get)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    RAW="$(trim_all "$RAW")"
    [[ -n "$RAW" ]] || { echo "❌ no key found for $ACCOUNT"; exit 1; }
    RAW_NO0X="${RAW#0x}"
    if [[ ! "$RAW_NO0X" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ stored key malformed (len ${#RAW_NO0X}). Use: $0 put $ACCOUNT 0x<64-hex>" >&2
      exit 1
    fi
    add_0x "$RAW_NO0X"
    ;;
  del)
    security delete-generic-password -a "$ACCOUNT" -s "$SERVICE" >/dev/null || true
    echo "🗑️  deleted ($SERVICE/$ACCOUNT)"
    ;;
  show)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    if [[ -z "$RAW" ]]; then echo "❌ no key found for $ACCOUNT"; exit 1; fi
    RAW_PRINTABLE="$(trim_all "$RAW")"
    RAW_NO0X="${RAW_PRINTABLE#0x}"
    echo "account=$ACCOUNT service=$SERVICE"
    echo "raw_len=${#RAW} printable_len=${#RAW_PRINTABLE} hex_len=${#RAW_NO0X}"
    # show any non-hex characters
    NONHEX="$(printf '%s' "$RAW_NO0X" | sed 's/[0-9a-fA-F]//g')"
    if [[ -n "$NONHEX" ]]; then echo "nonhex_chars_present: yes"; else echo "nonhex_chars_present: no"; fi
    ;;

  normalize)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    [[ -n "$RAW" ]] || { echo "❌ no key found for $ACCOUNT"; exit 1; }
    RAW_NO0X="$(trim_all "${RAW#0x}")"
    if [[ ! "$RAW_NO0X" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ cannot normalize: stored key is not 64 hex" >&2
      exit 1
    fi
    security add-generic-password -a "$ACCOUNT" -s "$SERVICE" -w "$RAW_NO0X" -U >/dev/null
    echo "✅ normalized ($SERVICE/$ACCOUNT) to 64 hex without 0x"
    ;;
  *)
    echo "Usage: $0 {put|get|del|show|normalize} <account> [privkey]"
    exit 1
    ;;
esac
#!/usr/bin/env bash
# Store/retrieve EVM hot key in macOS Keychain (Touch ID prompts enabled in Keychain Access).
# Adds robust normalization to avoid hidden characters from paste (zero-width, quotes, spaces, CR/LF).
# New commands:
#   put-stdin <account>        # secure prompt (no echo) to paste key; cleans & validates
#   test <account>             # prints derived address from stored key (without revealing key)
#   showhex <account>          # prints byte/hex diagnostics of stored value

set -euo pipefail

CMD="${1:-help}"
SERVICE="XO_HOT_EVM_PRIVKEY"
ACCOUNT="${2:-xo-hot}"

trim_all() {
  # remove spaces, tabs, CR/LF
  printf '%s' "$1" | tr -d '\r\n\t '
}

strip_0x() {
  local key="$1"
  echo "${key#0x}"
}

# Remove EVERYTHING that's not hex [0-9a-fA-F]
clean_hex() {
  LC_ALL=C tr -d -c '0-9a-fA-F' <<<"$1"
}

add_0x() {
  local key="$1"
  [[ "$key" == 0x* ]] && echo "$key" || echo "0x${key}"
}

put_impl() {
  local acct="$1"; shift
  local raw_in="$1"; shift || true
  local trimmed; trimmed="$(trim_all "$raw_in")"
  local no0x; no0x="$(strip_0x "$trimmed")"
  local cleaned; cleaned="$(clean_hex "$no0x")"

  # warn if characters were removed during cleaning
  if [[ "${#no0x}" -ne "${#cleaned}" ]]; then
    echo "ℹ️  removed $(( ${#no0x} - ${#cleaned} )) non-hex character(s) during normalization" >&2
  fi

  if [[ ! "$cleaned" =~ ^[0-9a-fA-F]{64}$ ]]; then
    echo "❌ invalid private key: need 64 hex chars (with or without 0x)" >&2
    exit 1
  fi
  security add-generic-password -a "$acct" -s "$SERVICE" -w "$cleaned" -U >/dev/null
  echo "✅ stored in keychain ($SERVICE/$acct, without 0x)"
}

case "$CMD" in
  put)
    KEY_HEX_RAW="${3:-}"
    [[ -n "$KEY_HEX_RAW" ]] || { echo "Usage: $0 put <account> <privkey>"; exit 1; }
    put_impl "$ACCOUNT" "$KEY_HEX_RAW"
    ;;

  put-stdin)
    # Secure prompt (no echo), avoids shell history. Paste the key and press Enter.
    echo -n "Paste private key for $ACCOUNT (will not echo): " >&2
    stty -echo
    read -r KEY_HEX_RAW || true
    stty echo
    echo >&2
    [[ -n "${KEY_HEX_RAW:-}" ]] || { echo "❌ empty input" >&2; exit 1; }
    put_impl "$ACCOUNT" "$KEY_HEX_RAW"
    ;;

  get)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    RAW="$(trim_all "$RAW")"
    [[ -n "$RAW" ]] || { echo "❌ no key found for $ACCOUNT"; exit 1; }
    RAW_NO0X="${RAW#0x}"
    # Clean again on read, just in case old value had hidden junk
    RAW_NO0X_CLEAN="$(clean_hex "$RAW_NO0X")"
    if [[ ! "$RAW_NO0X_CLEAN" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ stored key malformed (hex_len ${#RAW_NO0X_CLEAN}). Use: $0 put $ACCOUNT 0x<64-hex>" >&2
      exit 1
    fi
    add_0x "$RAW_NO0X_CLEAN"
    ;;

  del)
    security delete-generic-password -a "$ACCOUNT" -s "$SERVICE" >/dev/null || true
    echo "🗑️  deleted ($SERVICE/$ACCOUNT)"
    ;;

  show)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    if [[ -z "$RAW" ]]; then echo "❌ no key found for $ACCOUNT"; exit 1; fi
    RAW_PRINTABLE="$(trim_all "$RAW")"
    RAW_NO0X="${RAW_PRINTABLE#0x}"
    CLEAN="$(clean_hex "$RAW_NO0X")"
    echo "account=$ACCOUNT service=$SERVICE"
    echo "raw_len=${#RAW} printable_len=${#RAW_PRINTABLE} hex_len=${#CLEAN}"
    NONHEX="$(printf '%s' "$RAW_NO0X" | sed 's/[0-9a-fA-F]//g')"
    if [[ -n "$NONHEX" ]]; then echo "nonhex_chars_present: yes"; else echo "nonhex_chars_present: no"; fi
    ;;

  showhex)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    if [[ -z "$RAW" ]]; then echo "❌ no key found for $ACCOUNT"; exit 1; fi
    printf '%s' "$RAW" | hexdump -C
    ;;

  normalize)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    [[ -n "$RAW" ]] || { echo "❌ no key found for $ACCOUNT"; exit 1; }
    RAW_NO0X="$(trim_all "${RAW#0x}")"
    CLEAN="$(clean_hex "$RAW_NO0X")"
    if [[ ! "$CLEAN" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ cannot normalize: stored key is not 64 hex (hex_len ${#CLEAN})" >&2
      exit 1
    fi
    security add-generic-password -a "$ACCOUNT" -s "$SERVICE" -w "$CLEAN" -U >/dev/null
    echo "✅ normalized ($SERVICE/$ACCOUNT) to 64 hex without 0x"
    ;;

  test)
    RAW=$(security find-generic-password -a "$ACCOUNT" -s "$SERVICE" -w 2>/dev/null || true)
    [[ -n "$RAW" ]] || { echo "❌ no key found for $ACCOUNT"; exit 1; }
    CLEAN="$(clean_hex "${RAW#0x}")"
    if [[ ! "$CLEAN" =~ ^[0-9a-fA-F]{64}$ ]]; then
      echo "❌ stored key malformed (hex_len ${#CLEAN})" >&2; exit 1
    fi
    ADDR=$(env PK="0x$CLEAN" node --input-type=module -e 'import {Wallet} from "ethers"; console.log(new Wallet(process.env.PK).address)')
    echo "$ADDR"
    ;;

  *)
    cat >&2 <<USAGE
Usage: $0 {put|get|del|show|showhex|normalize|put-stdin|test} <account> [privkey]
  put         : store a key passed as argument (will normalize)
  put-stdin   : secure prompt (no echo), paste key, will normalize
  get         : print 0x + 64-hex
  show        : diagnostics about stored value lengths/characters
  showhex     : hexdump the stored value (for debugging hidden chars)
  normalize   : clean stored value in-place to 64-hex (no 0x)
  test        : print derived address from stored key
USAGE
    exit 1
    ;;
esac

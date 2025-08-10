#!/usr/bin/env bash
set -euo pipefail

# --- prereqs ---
# export CLOUDFLARE_API_TOKEN=REDACTED
# export NAMECHEAP_API_URL="https://api.namecheap.com/xml.response"
# export NAMECHEAP_API_USER=your_nc_api_user
# export NAMECHEAP_USERNAME=your_nc_username
# export NAMECHEAP_API_KEY=REDACTED
# export NAMECHEAP_CLIENT_IP=$(curl -s https://ifconfig.me)   # must be whitelisted in Namecheap

cf() { curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" "$@"; }

cf_zone_id() {
  local domain="$1"
  cf "https://api.cloudflare.com/client/v4/zones?name=${domain}&status=active" | jq -r '.result[0].id // empty'
}

cf_ns() {
  local zone_id="$1"
  cf "https://api.cloudflare.com/client/v4/zones/${zone_id}" | jq -r '.result.name_servers[]'
}

# Idempotent DNS upsert (A/AAAA/CNAME/TXT etc)
cf_upsert() {
  local zone_id="$1" name="$2" type="$3" content="$4" proxied="${5:-false}"
  local existing; existing=$(cf "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records?type=${type}&name=${name}")
  local id; id=$(echo "$existing" | jq -r '.result[0].id // empty')
  if [[ -n "$id" ]]; then
    cf -X PUT "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records/${id}" \
      --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied}" | jq '{updated:.success,name:"'"$name"'",type:"'"$type"'",proxied:'"$proxied"'}'
  else
    cf -X POST "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records" \
      --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied}" | jq '{created:.success,name:"'"$name"'",type:"'"$type"'",proxied:'"$proxied"'}'
  fi
}

# Namecheap: set registrar nameservers to Cloudflare’s for the given domain
nc_set_ns() {
  local domain="$1" ns1="$2" ns2="$3"
  local sld; sld=$(echo "$domain" | cut -d. -f1)
  local tld; tld=$(echo "$domain" | cut -d. -f2-)
  curl -sG "$NAMECHEAP_API_URL" \
    --data-urlencode "ApiUser=$NAMECHEAP_API_USER" \
    --data-urlencode "ApiKey=$NAMECHEAP_API_KEY" \
    --data-urlencode "UserName=$NAMECHEAP_USERNAME" \
    --data-urlencode "ClientIp=$NAMECHEAP_CLIENT_IP" \
    --data-urlencode "Command=namecheap.domains.dns.setCustom" \
    --data-urlencode "SLD=$sld" \
    --data-urlencode "TLD=$tld" \
    --data-urlencode "Nameservers=$ns1,$ns2" \
    | xmllint --format - 2>/dev/null | sed -n '1,6p'
}

# --- one-shot: sync registrar NS to Cloudflare for a domain ---
sync_ns_to_cf() {
  local domain="$1"
  echo "🔎 Fetching Cloudflare zone for ${domain}…"
  local zid; zid=$(cf_zone_id "$domain")
  if [[ -z "$zid" ]]; then
    echo "❌ No active zone found in Cloudflare for ${domain}. Create the zone first."
    return 1
  fi
  echo "✅ Zone ID: $zid"
  mapfile -t ns < <(cf_ns "$zid")
  if [[ "${#ns[@]}" -lt 2 ]]; then
    echo "❌ Could not read CF nameservers."
    return 1
  fi
  echo "🌐 Cloudflare nameservers: ${ns[*]}"
  echo "📝 Updating Namecheap registrar NS…"
  nc_set_ns "$domain" "${ns[0]}" "${ns[1]}"
  echo "⏳ Propagation may take 5–30 mins."
}

# --- examples ---
# 1) Set registrar NS for xo-vault.com to Cloudflare:
# sync_ns_to_cf xo-vault.com
#
# 2) After zone is active, create DNS records:
# zid=$(cf_zone_id 21xo.com)
# cf_upsert "$zid" docs.21xo.com CNAME xo-verses.github.io false
# cf_upsert "$zid" _github-pages-challenge-xo-verses.docs.21xo.com TXT 345b996dfda97fb0d2a23759003221 false
# cf_upsert "$zid" digest.21xo.com CNAME workers.dev true

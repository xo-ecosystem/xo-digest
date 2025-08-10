#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE=${1:-dns_config.yml}

# --- Prereqs ---
# export CLOUDFLARE_API_TOKEN=REDACTED
# export NAMECHEAP_API_URL="https://api.namecheap.com/xml.response"
# export NAMECHEAP_API_USER=your_nc_api_user
# export NAMECHEAP_USERNAME=your_nc_username
# export NAMECHEAP_API_KEY=REDACTED
# export NAMECHEAP_CLIENT_IP=$(curl -s https://ifconfig.me)

cf() { curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" "$@"; }

cf_zone_id() {
  local domain="$1"
  cf "https://api.cloudflare.com/client/v4/zones?name=${domain}&status=active" | jq -r '.result[0].id // empty'
}

cf_ns() {
  local zone_id="$1"
  cf "https://api.cloudflare.com/client/v4/zones/${zone_id}" | jq -r '.result.name_servers[]'
}

cf_upsert() {
  local zone_id="$1" name="$2" type="$3" content="$4" proxied="${5:-false}"
  local existing; existing=$(cf "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records?type=${type}&name=${name}")
  local id; id=$(echo "$existing" | jq -r '.result[0].id // empty')
  if [[ -n "$id" ]]; then
    cf -X PUT "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records/${id}" \
      --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied}" \
      | jq '{updated:.success,name:"'"$name"'",type:"'"$type"'",proxied:'"$proxied"'}'
  else
    cf -X POST "https://api.cloudflare.com/client/v4/zones/${zone_id}/dns_records" \
      --data "{\"type\":\"$type\",\"name\":\"$name\",\"content\":\"$content\",\"proxied\":$proxied}" \
      | jq '{created:.success,name:"'"$name"'",type:"'"$type"'",proxied:'"$proxied"'}'
  fi
}

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

sync_domain() {
  local domain="$1"
  echo "🔎 Fetching Cloudflare zone for ${domain}…"
  local zid; zid=$(cf_zone_id "$domain")
  if [[ -z "$zid" ]]; then
    echo "❌ No active zone found for ${domain}."
    return 1
  fi
  mapfile -t ns < <(cf_ns "$zid")
  echo "🌐 Cloudflare nameservers: ${ns[*]}"
  echo "📝 Updating registrar NS via Namecheap API…"
  nc_set_ns "$domain" "${ns[0]}" "${ns[1]}"
}

# --- Parse YAML using yq ---
parse_yaml_and_apply() {
  local cfg="$1"
  local domain_count
  domain_count=$(yq '.domains | length' "$cfg")
  for i in $(seq 0 $((domain_count - 1))); do
    local domain; domain=$(yq -r ".domains[$i].name" "$cfg")
    echo "=============================="
    echo "🌍 Processing $domain"
    sync_domain "$domain"

    local zid; zid=$(cf_zone_id "$domain")
    local record_count; record_count=$(yq ".domains[$i].records | length" "$cfg")
    for j in $(seq 0 $((record_count - 1))); do
      local type; type=$(yq -r ".domains[$i].records[$j].type" "$cfg")
      local name; name=$(yq -r ".domains[$i].records[$j].name" "$cfg")
      local content; content=$(yq -r ".domains[$i].records[$j].content" "$cfg")
      local proxied; proxied=$(yq -r ".domains[$i].records[$j].proxied" "$cfg")
      cf_upsert "$zid" "$name.$domain" "$type" "$content" "$proxied"
    done
  done
}

parse_yaml_and_apply "$CONFIG_FILE"

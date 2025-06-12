#!/bin/bash
# Cloudflare API DNS automation script for XO Mail setup

CF_API_TOKEN="2Q3UXcYjc73UQUv27Aafz6d0SC-7YsEc3V0Gb4J1"
ZONE_ID="022ef10fb9675e3b3a375b1cc95e92a6"
ZONE_NAME="21xo.com"

# Add MX record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"MX","name":"21xo.com","content":"hosted.mailcow.de","priority":10,"ttl":3600,"proxied":false}'

# Add SPF record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"TXT","name":"21xo.com","content":"v=spf1 mx include:hosted.mailcow.de ~all","ttl":3600,"proxied":false}'

# Add DMARC record
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
     -H "Authorization: Bearer $CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"TXT","name":"_dmarc","content":"v=DMARC1; p=quarantine; rua=mailto:marco@21xo.com; adkim=s; aspf=s","ttl":3600,"proxied":false}'

echo "✅ DNS update commands for Mailcow have been submitted to Cloudflare."

# fab_tasks/cloudflare_dns.py
from invoke import task
import requests
import os

CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ZONE_ID = os.environ.get("CLOUDFLARE_ZONE_ID")
HEADERS = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

@task
def ensure_dns(c, dry_run=False):
    """Ensure Cloudflare DNS records exist for all subdomains"""
    base_domain = "21xo.com"
    subdomains = ["vault", "inbox", "preview", "agent0"]
    cname_target = ".fly.dev"

    for sub in subdomains:
        fqdn = f"{sub}.{base_domain}"
        target = f"{sub}-21xo{cname_target}"

        print(f"🔍 Checking record: {fqdn} -> {target}")

        # Get existing DNS records
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records?type=CNAME&name={fqdn}"
        response = requests.get(url, headers=HEADERS)
        result = response.json()

        if result.get("result"):
            print(f"✅ CNAME already exists for {fqdn}")
            continue

        if dry_run:
            print(f"🌐 [Dry-run] Would create CNAME {fqdn} -> {target}")
            continue

        # Create DNS record
        create_url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
        data = {
            "type": "CNAME",
            "name": fqdn,
            "content": target,
            "ttl": 300,
            "proxied": True
        }
        create_resp = requests.post(create_url, headers=HEADERS, json=data)

        if create_resp.status_code == 200:
            print(f"✅ Created CNAME: {fqdn} -> {target}")
        else:
            print(f"❌ Failed to create CNAME: {create_resp.text}")


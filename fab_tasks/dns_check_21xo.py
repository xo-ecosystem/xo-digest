import os
import yaml
import requests
import socket
import dns.resolver
import json
from datetime import datetime
from invoke import Collection, task

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")  # Set this in your environment
ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID")  # Also set this

CLOUDFLARE_API_BASE = (
    f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
)


def list_services_from_compose(path="docker-compose.yml"):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("services", {}).keys()


def check_dns_record_exists(subdomain):
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    params = {"type": "CNAME", "name": f"{subdomain}.21xo.com"}
    r = requests.get(CLOUDFLARE_API_BASE, headers=headers, params=params)
    return r.json().get("result", [])


def create_cname_record(subdomain, target):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "type": "CNAME",
        "name": f"{subdomain}.21xo.com",
        "content": target,
        "ttl": 3600,
        "proxied": True,
    }
    return requests.post(CLOUDFLARE_API_BASE, headers=headers, json=data)


def validate_dns_resolution(domain):
    """Validate DNS resolution for a domain."""
    try:
        # Try to resolve the domain
        ip = socket.gethostbyname(domain)
        return True, ip
    except socket.gaierror:
        return False, None


def check_cname_chain(domain):
    """Check CNAME chain for a domain."""
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        cnames = [str(answer) for answer in answers]
        return True, cnames
    except Exception:
        return False, []


@task
def check_dns(c, dry_run=False, log_only=False, validate_resolution=True):
    """
    Check and optionally create DNS records for all services in docker-compose.yml.

    Args:
        dry_run (bool): Only show what would happen, don't perform writes.
        log_only (bool): Suppress printing to stdout, only log results.
        validate_resolution (bool): Validate DNS resolution for existing records.
    """

    def log(msg):
        if not log_only:
            print(msg)

    services = list_services_from_compose()
    log(f"🔍 Checking DNS for {len(services)} services...")

    results = []

    for service in services:
        domain = f"{service}.21xo.com"
        log(f"\n🔍 Checking DNS for {domain}")

        existing = check_dns_record_exists(service)

        if existing:
            log(f"✅ Found: {domain} already exists")

            if validate_resolution:
                # Validate DNS resolution
                resolves, ip = validate_dns_resolution(domain)
                if resolves:
                    log(f"  🌐 Resolves to: {ip}")
                else:
                    log(f"  ⚠️ DNS resolution failed")

                # Check CNAME chain
                has_cname, cnames = check_cname_chain(domain)
                if has_cname:
                    log(f"  🔗 CNAME chain: {' → '.join(cnames)}")
                else:
                    log(f"  ⚠️ No CNAME record found")

        else:
            log(f"⚠️ Missing: {domain} → would create CNAME → vault-21xo.fly.dev")
            if not dry_run:
                resp = create_cname_record(service, "vault-21xo.fly.dev")
                if resp.ok:
                    log(f"✅ Created CNAME for {domain}")
                else:
                    log(f"❌ Failed to create DNS: {resp.text}")
            else:
                log(f"ℹ️ Dry-run: would create CNAME for {domain} → vault-21xo.fly.dev")

        results.append(
            {
                "service": service,
                "domain": domain,
                "exists": bool(existing),
                "resolves": validate_dns_resolution(domain)[0] if existing else False,
            }
        )

    # Summary
    existing_count = sum(1 for r in results if r["exists"])
    resolving_count = sum(1 for r in results if r["resolves"])

    log(f"\n📊 DNS Summary:")
    log(f"  Total services: {len(services)}")
    log(f"  Existing records: {existing_count}")
    log(f"  Resolving: {resolving_count}")
    log(f"  Missing: {len(services) - existing_count}")

    return results


@task
def validate_all_subdomains(c, dry_run=False):
    """
    Validate all subdomains from .env.production and docker-compose.yml.

    Args:
        dry_run (bool): Only show what would be validated, don't perform checks.
    """

    def log(msg):
        print(msg)

    # Get services from docker-compose.yml
    services = list_services_from_compose()

    # Expected subdomains from environment
    expected_subdomains = [
        "vault.21xo.com",
        "inbox.21xo.com",
        "preview.21xo.com",
        "agent0.21xo.com",
    ]

    log(f"🔍 Validating {len(expected_subdomains)} expected subdomains...")

    validation_results = []

    for domain in expected_subdomains:
        log(f"\n🔍 Validating {domain}")

        if dry_run:
            log(f"  ℹ️ Dry-run: would validate {domain}")
            continue

        # Check DNS resolution
        resolves, ip = validate_dns_resolution(domain)
        if resolves:
            log(f"  ✅ Resolves to: {ip}")
        else:
            log(f"  ❌ DNS resolution failed")

        # Check CNAME chain
        has_cname, cnames = check_cname_chain(domain)
        if has_cname:
            log(f"  🔗 CNAME chain: {' → '.join(cnames)}")
        else:
            log(f"  ⚠️ No CNAME record found")

        # Check HTTP response
        try:
            response = requests.get(f"https://{domain}", timeout=5)
            log(f"  🌐 HTTP: {response.status_code}")
        except Exception as e:
            log(f"  ❌ HTTP failed: {e}")

        validation_results.append(
            {
                "domain": domain,
                "resolves": resolves,
                "ip": ip,
                "has_cname": has_cname,
                "cnames": cnames,
            }
        )

    return validation_results


@task
def sync_env_subdomains(c, dry_run=False):
    """
    Sync subdomains from docker-compose.yml to .env.production.

    Args:
        dry_run (bool): Only show what would be synced, don't perform writes.
    """

    def log(msg):
        print(msg)

    services = list_services_from_compose()

    # Generate environment variables
    env_vars = {}
    for service in services:
        env_key = f"XO_{service.upper()}_URL"
        env_value = f"https://{service}.21xo.com"
        env_vars[env_key] = env_value

    log(f"🔧 Syncing {len(env_vars)} environment variables...")

    for key, value in env_vars.items():
        log(f"  {key}={value}")

    if not dry_run:
        # Read existing .env.production
        env_file = ".env.production"
        env_content = ""

        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                env_content = f.read()

        # Add or update variables
        lines = env_content.split("\n")
        updated_lines = []
        existing_keys = set()

        for line in lines:
            if "=" in line:
                key = line.split("=")[0].strip()
                existing_keys.add(key)
                if key in env_vars:
                    updated_lines.append(f"{key}={env_vars[key]}")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add new variables
        for key, value in env_vars.items():
            if key not in existing_keys:
                updated_lines.append(f"{key}={value}")

        # Write back
        with open(env_file, "w") as f:
            f.write("\n".join(updated_lines))

        log(f"✅ Updated {env_file}")
    else:
        log(f"ℹ️ Dry-run: would update .env.production")

    return env_vars


@task
def generate_dns_history(c):
    """
    📜 Generate /public/dns-history.json with timestamped DNS validity entries.
    """
    from pathlib import Path

    deploy_log_path = Path(".deploy-log.json")
    output_path = Path("public/dns-history.json")

    if not deploy_log_path.exists():
        print("❌ No .deploy-log.json found")
        return

    try:
        with deploy_log_path.open("r") as f:
            logs = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load deploy log: {e}")
        return

    dns_entries = []
    for entry in logs:
        if "dns" in entry and "valid" in entry["dns"]:
            dns_entries.append(
                {
                    "timestamp": entry.get("timestamp", datetime.utcnow().isoformat()),
                    "valid": entry["dns"]["valid"],
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(dns_entries, f, indent=2)

    print(f"✅ Generated DNS history with {len(dns_entries)} entries → {output_path}")


@task
def generate_dns_chart_html(c):
    """
    📊 Generate /public/dns-history-chart.html using /public/dns-history.json as input
    """
    import json
    from pathlib import Path

    data_path = Path("public/dns-history.json")
    output_path = Path("public/dns-history-chart.html")

    if not data_path.exists():
        print("❌ No dns-history.json found")
        return

    with data_path.open("r") as f:
        dns_data = json.load(f)

    # Prepare labels and data lists as JS array literals
    labels = [entry["timestamp"] for entry in dns_data]
    data_values = [1 if entry["valid"] else 0 for entry in dns_data]
    js_labels = json.dumps(labels)
    js_data = json.dumps(data_values)

    chart_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>DNS History Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="dnsChart" width="800" height="300"></canvas>
    <script>
        const ctx = document.getElementById('dnsChart').getContext('2d');
        const data = {{
            labels: {js_labels},
            datasets: [{{
                label: 'DNS Validity',
                data: {js_data},
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: true
            }}]
        }};
        new Chart(ctx, {{
            type: 'line',
            data: data,
            options: {{
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1,
                            callback: function(value) {{
                                return value === 1 ? 'Valid' : 'Invalid';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """

    output_path.write_text(chart_html)
    print(f"✅ Generated DNS chart HTML → {output_path}")


@task
def generate_all_dns_artifacts(c):
    """
    🔁 Run both DNS history and chart generation tasks.
    """
    generate_dns_history(c)
    generate_dns_chart_html(c)


# Create namespace
ns = Collection("dns")
ns.add_task(check_dns, "check")
ns.add_task(validate_all_subdomains, "validate")
ns.add_task(sync_env_subdomains, "sync")
ns.add_task(generate_dns_history, "history")
ns.add_task(generate_dns_chart_html, "chart")
ns.add_task(generate_all_dns_artifacts, "artifacts")

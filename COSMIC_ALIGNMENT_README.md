import os
import requests

CLOUDFLARE_API_TOKEN = os.getenv("CF_API_TOKEN")
CLOUDFLARE_ZONE_ID = os.getenv("CF_ZONE_ID")
CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"

def create_dns_record(domain, name, ip="1.1.1.1"):
headers = {
"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
"Content-Type": "application/json",
}
payload = {
"type": "A",
"name": name,
"content": ip,
"ttl": 3600,
"proxied": True
}
resp = requests.post(
f"{CLOUDFLARE_API_BASE}/zones/{CLOUDFLARE_ZONE_ID}/dns_records",
headers=headers,
json=payload,
)
return resp.status_code == 200, resp.json()

@task
def correct_dns(c):
print("🛠 Attempting to auto-correct DNS records using Cloudflare API...")
for name, domain in SERVICES.items():
try:
dns.resolver.resolve(domain, "A")
print(f"✅ {domain} already resolves.")
except:
print(f"⚠️ {domain} missing - creating via Cloudflare...")
subdomain = domain.split(".")[0]
success, result = create_dns_record(domain, subdomain)
if success:
print(f"✅ {domain} created successfully.")
else:
print(f"❌ Failed to create {domain}: {result}")

# 🌌 XO Core – Cosmic Alignment System

This document describes the full deployment, DNS management, and dashboard visualization pipeline powering the XO Core ecosystem.

---

## ✅ System Components

| Component                               | Description                                                   |
| --------------------------------------- | ------------------------------------------------------------- |
| `fabfile.py`                            | Central Fabric task loader with namespace wiring              |
| `dns_check_21xo.py`                     | Cloudflare DNS checker, resolver, and artifact generator      |
| `deploy.py`                             | Fly.io deploy automation, rollback, health-check, and logging |
| `dashboard/`                            | React dashboard with `/status` route for live deploy views    |
| `.github/workflows/deploy_with_dns.yml` | CI pipeline triggered on Git push                             |

---

## 🚀 Key Fabric Commands

```bash
# Full system dry-run alignment
fab cosmic-align --dry-run

# Actual deploy to Fly + DNS validation
fab deploy.with_dns

# Check DNS records and resolutions
fab dns.check --dry-run

# Generate and sync dashboard artifacts
fab dns.artifacts
fab dashboard.sync

# Log current deploy status per service
fab deploy.log --service=vault

# Bundle patch for current session
fab patch.bundle
```

---

## 🌐 Dashboard Features

- ✅ Service status (live from `.deploy-log.json`)
- 📈 DNS validity chart (from `dns-history.json`)
- 🔍 Filtering and sorting per service
- 🛠 Log-level export as `.json` or `.csv`
- 🔄 Auto-refresh every 5 seconds

See it live at: `/status` or embedded via `<iframe src="/dns-history-chart.html">`

---

## 🔁 CI/CD Pipeline Flow

1. Git push to `main`
2. Trigger: `.github/workflows/deploy_with_dns.yml`
3. Run: `fab deploy.with_dns`
4. Auto-update:
   - `.deploy-log.json`
   - `dns-history.json`
   - `dns-history-chart.html`
5. Auto-commit and push
6. React dashboard reflects latest status

---

## 📁 Output Artifacts

| File                            | Purpose                             |
| ------------------------------- | ----------------------------------- |
| `.deploy-log.json`              | Source of truth for deploy metadata |
| `public/dns-history.json`       | Time series of DNS validity         |
| `public/dns-history-chart.html` | ChartJS-based visual render         |
| `logs/`                         | Optional per-task log output        |
| `patch_bundle/`                 | Auto-bundled patches for GitHub     |

---

## 🧪 Testing the System

```bash
# Run all checks and generate visual output
fab cosmic-align
fab dns.artifacts

# Commit artifacts manually (if needed)
git add public/ .deploy-log.json
git commit -m "🔄 Dashboard sync"
```

---

## 🧭 Summary

The XO Core ecosystem now features a complete **cosmic alignment system** that ensures:

- Automated deployment
- DNS validation + self-correction
- Real-time dashboard views
- Charted deploy history
- Rollback-ready deploy logs

Ready for production and expansion.

---</file>

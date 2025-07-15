

# 🧪 XO Fabric Diagnostic Cheatsheet

## 🚀 Direct CLI Usage (dynamic_loader.py)

| Command | Description |
|--------|-------------|
| `python dynamic_loader.py --diagnose` | Basic diagnostics |
| `--export=summary.md` | Save as Markdown |
| `--export=summary.json` | Save as JSON |
| `--pulse-bundle` | Generate `.mdx` bundle |
| `--upload=ipfs` | Upload to IPFS |
| `--upload=arweave` | Upload to Arweave |
| `--verbose` | Enable detailed logs |

## 🧵 Fabric (xo-fab) Tasks

| Task | Description |
|------|-------------|
| `xo-fab diagnose` | Run diagnostics (default) |
| `--export=reports/loader.md` | Save Markdown |
| `--export=reports/loader.json` | Save JSON |
| `--pulse-bundle` | Create Pulse Bundle |
| `--upload=ipfs` / `--upload=arweave` | Cloud upload |
| `xo-fab diagnose.report` | Full diagnostic report |
| `--path=vault/reports/loader.md` | Export custom path |

## 🧪 CI/CD & Automation

| Task | Description |
|------|-------------|
| `xo-fab diagnose.ci` | CI-friendly output |
| `xo-fab diagnose.vault` | Vault checks |
| `xo-fab diagnose.production` | Prod-readiness |
| `xo-fab diagnose.real_world` | Real-case simulations |
| `xo-fab diagnose.webhook_test` | Webhook ping |
| `xo-fab diagnose.github_test` | GitHub issue test |

## 🔧 Advanced Features

- Simulate missing tasks, circular imports, mock services
- CI Integration: GitHub Actions, Webhook, JSON logs
- Vault Sync: Reports exportable as pulses
- Auto-Fix: Detect and optionally patch broken imports or tasks
- Upload Options: Arweave / IPFS with CID tracking
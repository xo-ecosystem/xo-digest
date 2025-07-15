

# 🌀 XO Pulse Publishing Workflows

This directory contains GitHub Actions used to automate the publishing, syncing, and digesting of XO Pulses.

## Available Workflows

### 🔁 `pulse-prod.yml`
- **Trigger**: Manual or push to specific branches (e.g. `pulse/*`)
- **Steps**:
  1. 🛠️ Setup Python environment
  2. 🧪 Dry-run test using `pulse_publish.py --dry-run`
  3. 🚀 Real publish via `pulse_publish.py --prod`
  4. 📡 Digest webhook trigger (`xo-digest.pages.dev/api/trigger`)
  5. 📬 Telegram notification
  6. ♻️ Shared logic via `xo-verses/xo-digest/.github/workflows/digest.yml`

### ♻️ `digest.yml`
- **Purpose**: Reusable component for consistent digest formatting and sync
- **Inputs**:
  - `pulse_slug`: e.g. `seventh_seal`
  - `mode`: `dry-run`, `preview`, `prod`
  - `webhook_url` (optional)

## Setup

- Set the following secrets in your GitHub repo:
  - `XO_TELEGRAM_BOT_TOKEN`
  - `XO_TELEGRAM_CHANNEL_ID`
  - `XO_DIGEST_WEBHOOK`
  - `ARWEAVE_KEY_JSON`
  - `PULSE_ENV` (optional: `prod`/`staging`)

## Status Badges

Add this badge to your main README:

```markdown
![XO Pulse Publish](https://github.com/xo-core/xo-core/actions/workflows/pulse-prod.yml/badge.svg)
```
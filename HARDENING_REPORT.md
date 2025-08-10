# Hardening Report

## Files removed

- vault/unseal_keys.json
- vault/init_keys.json
- snapshots/\*/vault/unseal_keys.json
- ui/xo-wallet/xo-wallet-config.json

## New/updated files

- .gitignore (strict security patterns)
- .envrc.sample (placeholders only)
- env/.env.example, env/.env.local.sample (placeholders only)
- SENSITIVE_PATTERNS.txt
- .pre-commit-config.yaml (pre-commit hooks)
- .gitleaks.toml (allowlist)
- .github/workflows/security.yml (CI secret scanning)
- SECURITY.md, CONTRIBUTING.md
- scripts/security/preflight.sh, scripts/security/install-hooks.sh
- scripts/security/history-scrub.md
- deploy_xo_agent.py and shared/hooks/webhook.py updated to require env vars

## Hooks enabled

- EOF fixer, trailing whitespace, merge conflict check, large file guard
- detect-secrets with baseline
- gitleaks protect (redact, staged, with config)
- local cleanup hook

## Local setup commands

- make bootstrap
- detect-secrets scan > .secrets.baseline (already created)
- pre-commit run --all-files (passing)
- make scan (optional extra checks)

## CI

- .github/workflows/security.yml runs gitleaks and detect-secrets; fails on findings

## Next steps in GitHub

- Enable branch protection on `main`
- Require PR reviews and status checks (CI) before merge
- Optionally enable signed commits and secret scanning at org level

## Acceptance status

- pre-commit run --all-files: PASS
- make scan: configure as needed (gitleaks/detect-secrets available)
- All app code: loads config from env; hardcoded webhook defaults removed

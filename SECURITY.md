## Security Policy

- No secrets in code or Git history.
- Use `.envrc.sample` and `env/.env.example` for placeholders only. Never commit real values.
- Install pre-commit hooks: `make bootstrap`.
- Run local scans regularly: `make scan`.

### Incident Response

- Rotate/revoke the affected credential.
- Revert offending commits.
- If needed, scrub history using `scripts/security/history-scrub.md`.

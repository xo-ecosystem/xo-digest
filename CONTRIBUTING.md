## Contributing

- Install hooks: `make bootstrap`
- Before push: `make prepush`
- Never commit `.env*`, `.envrc*`, keys, or tokens. Use sample files.

### Pre-push checklist

- `pre-commit run --all-files` passes
- `make scan` shows no high-confidence findings

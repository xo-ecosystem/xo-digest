# XO Audit: Option B (Merkle + Daily Manifest + Transit Sign)

## One-time setup

```bash
vault secrets enable transit 2>/dev/null || true
vault write -f transit/keys/xo-audit type=ed25519 exportable=false allow_plaintext_backup=false
vault read -field=public_key transit/keys/xo-audit > config/keys/xo-audit.pub

Daily flow

# Load envs (from Agent or one-shot renderer)
set -a; source /tmp/xo-env.sh; set +a
# or:
./scripts/render_xo_env.sh && set -a; source /tmp/xo-env.sh; set +a

# Write some events + manifest
xo-fab audit.write_test
# Verify
xo-fab audit.verify --prefix audit/$(date -u +%Y-%m-%d)
# Badge
xo-fab audit.badge --prefix audit/$(date -u +%Y-%m-%d)

Tools
	•	scripts/audit_build_and_upload.py — build Merkle, sign via Transit, upload artifacts + manifest.
	•	scripts/audit_verify.py — recompute Merkle, verify signature with Transit.
	•	scripts/audit_diff.py — compare two manifests.
	•	scripts/audit_badge.py — generate status.svg with object count + date.
	•	scripts/audit_rotate_transit.py — rotate Transit key.

Notes
	•	Keep writer S3 key PutObject-only (no deletes) and separate read-only creds for auditors/UI.
	•	Paths are append-only, use unique keys under audit/YYYY-MM-DD/objects/....
	•	Transit key rotation embeds key_version in manifest.json, so verifiers stay compatible.


```

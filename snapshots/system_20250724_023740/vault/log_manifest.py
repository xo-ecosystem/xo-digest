@task
def vault_log_manifest(c):
    """📄 Write MDX manifest summarizing Vault bootstrap to logbook."""
    from datetime import datetime
    mdx_path = Path("vault/logbook/vault_bootstrap.mdx")
    mdx_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    content = f"""---
title: Vault Bootstrap
date: {now}
tags: [vault, bootstrap, automation]
---

**Vault Bootstrap Log**

- Status: ✅ Initialized
- Tag: `v0.2.0-vault-automation`
- Files: `vault/.keys.enc`, `vault/unseal_keys.json`
- Tasks Run: `vault.pull_secrets`, `vault.unseal`, `vault.status`
- ZIP: `vault_automation.zip`

✍️ Generated at {now}
"""
    with open(mdx_path, "w") as f:
        f.write(content)
    print(f"✅ Manifest written: {mdx_path}")
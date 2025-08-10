# ✅ XO Vault Verifiable Storychain — TODO Checklist (2025-08-04)

- [ ] 🛠️ Scaffold a hybrid `Makefile` with 10 most common tasks from xo-fab
- [ ] 🔧 Refactor fragile `xo-fab` tasks into standalone `scripts/*.py` (non-breaking)
- [ ] 🧪 Generate a `cli.py` runner using `argparse` interface (future CLI)
- [ ] ✅ Scaffold `.env.template` and safe `.env.production` for GitHub Actions
- [ ] 📁 Organize drop bundles into `drops/drafts/` vs `drops/sealed/` folders
- [ ] 🛡️ Add `xo-fab verify.drop:<drop>` task to verify Vault trust (multi-node)
- [ ] ⛓️ Implement Option A - Chain-of-trust logic for verifiable storychain:
- [ ]     • Add `previous_hash` field to `.meta.yml` / `.status.json`
- [ ]     • Compute SHA256 of `.mdx` + `.meta.yml` + asset, store in metadata
- [ ]     • Sign using Vault key and log to `vault/digest/chain.log`
- [ ] 📌 Prepare for Option B - `/vault/chain/index.json` explorer upgrade

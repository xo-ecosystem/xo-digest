# 🧪 XO Core Cheat Sheet

## 🔧 Fabric Task Namespaces

| Namespace | Description                        | Example Task              |
| --------- | ---------------------------------- | ------------------------- |
| dns       | DNS management + resolution checks | `fab dns.check --dry-run` |
| deploy    | Deploy and Fly.io config           | `fab deploy.test`         |
| vault     | Vault service tasks                | `fab vault.sync`          |
| pulse     | Pulse publishing + sync            | `fab pulse.sync`          |
| drops     | Drop metadata + previews           | `fab drops.render`        |
| digest    | Digest bundle + update             | `fab digest.publish`      |
| summary   | System overview + reports          | `fab summary.generate`    |
| patch     | Patch bundle create/apply          | `fab patch.bundle`        |
| loader    | Dynamic loader + introspection     | `fab loader.list`         |

## 🚀 Make Targets

| Target              | Description                             |
| ------------------- | --------------------------------------- |
| `make cosmic-align` | Run full alignment + deploy validation  |
| `make dns-check`    | Check DNS records for all services      |
| `make deploy-test`  | Test all deploys and verify endpoints   |
| `make patch-bundle` | Create a patch bundle with logs/summary |

## 🔐 DNS Subdomains (Expected)

- `vault.21xo.com`
- `preview.21xo.com`
- `agent0.21xo.com`
- `inbox.21xo.com`

## 📁 Patch Bundle Output

```bash
patch_bundle/xo_core_patch_<timestamp>/
├── changes.patch
├── task_summary_<timestamp>.md
├── logs/
└── xo_core_patch_<timestamp>.zip
```

## 🧪 Test Deploy

```bash
fab deploy.test --dry-run
fab deploy.health --service=inbox
```

## 🛰️ Namespace Discovery

```bash
fab loader.load --namespace=all
fab loader.list
```

---

XO Core is now **cosmically aligned**. Ready for the stars. ✨

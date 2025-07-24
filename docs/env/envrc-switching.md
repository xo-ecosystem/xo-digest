# 🔁 XO `.envrc` Switcher & Relinker

Enable seamless switching between environment setups (e.g., XO vs legacy FAB2), with safety fallback and auto-relinking for `.envrc.link`. Ensures smooth DX across projects using `direnv`.

## 🗂 File Conventions

| File            | Purpose                                     |
| --------------- | ------------------------------------------- |
| `.envrc`        | Auto-loaded by `direnv`, symlink to `.link` |
| `.envrc.link`   | Controlled symlink to real `.envrc*` files  |
| `.envrc.fab2`   | Legacy Fabric 2 environment config          |
| `.envrc` (real) | Fallback file if `.envrc.link` missing      |

## 🧰 Fabric Tasks

### 1. `xo-fab env.switch`

```bash
xo-fab env.switch --mode=xo|fab2|link [--apply]
```

- Switches `.envrc.link` to:
  - `.envrc` (default XO mode)
  - `.envrc.fab2` (legacy mode)
  - `.envrc.link` (explicit relink)
- `--apply`: force link `.envrc → .envrc.link` and run `direnv allow`
- Handles:
  - 🧹 Cleaning broken symlinks
  - ✅ Logs updated status

### 2. `xo-fab env.relink`

```bash
xo-fab env.relink
```

- Recreates `.envrc.link → .envrc` if:
  - Link is broken
  - File is stale
- Logs successful relink or error if missing fallback

## 🧪 Examples

```bash
xo-fab env.switch --mode=fab2 --apply
xo-fab env.relink
```

## 🧭 Future Ideas

| Feature                       | Status     | Notes                                                                   |
| ----------------------------- | ---------- | ----------------------------------------------------------------------- |
| `xo-fab env.status`           | 🔜 Planned | Print the current `.envrc.link → target` with link health check         |
| `xo-fab env.edit`             | 🧪 Draft   | Opens the current `.envrc.link` target in `$EDITOR`                     |
| `xo-fab env.template`         | 🔜 Planned | Generate `.envrc.link` from `.envrc.link.template` if missing           |
| `xo-fab env.ensure`           | 🧪 Draft   | Ensure `.envrc.link` exists and relinks if invalid                      |
| `.envrc.link.default` support | 🔜 Planned | Fallback logic if target is undefined or missing                        |
| Git-aware `.envrc` switching  | ❌         | Auto switch based on Git branch or tag (e.g., main → XO, legacy → fab2) |
| VSCode direnv extension hook  | ❌         | Auto-run `env.switch` or `direnv allow` from VSCode launch              |

---

🧩 Used for onboarding, CI/CD, or fallback resolution in hybrid Fabric environments.

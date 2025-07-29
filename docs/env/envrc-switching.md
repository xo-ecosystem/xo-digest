# Envrc Switching

This guide explains how to manage multiple `.envrc` configurations within the XO Core system using helper commands and symlink logic. It enables developers to seamlessly switch environments depending on which toolset (Fabric v1 or v2) or context (local, production) they're using.

## 🔀 Switching Environments

XO Core supports `.envrc.<name>` variants like:

- `.envrc.fab1` → For Fabric v1 compatibility
- `.envrc.fab2` → For Fabric v2+ enhanced task loading
- `.envrc.link` → Symlink target (active configuration)

Use the CLI helper:

```bash
xo-fab env.switch fab2
```

This command:

- Backs up the current `.envrc`
- Links the selected `.envrc.<name>` to `.envrc`
- Reloads direnv and environment variables

## ♻️ Auto-Restore Fallback

If `.envrc` is missing or broken, you can relink the last known working configuration:

```bash
xo-fab env.relink
```

This tries to re-establish the symlink to `.envrc.link`.

## 🌱 Onboarding Tips (for Brie or non-devs)

- Use Cursor or VS Code to view project structure
- Avoid editing `.envrc` directly — use the CLI helpers
- The active environment is visible via:

  ```bash
  xo-fab env.status
  ```

- When switching, Cursor might prompt to reload open files — accept the reload
- After switching, re-run:

  ```bash
  direnv reload
  ```

## 🧪 Diagnostics

To verify a working environment setup:

```bash
xo-fab env.diagnose
```

This reports any issues with Python paths, `.envrc` links, or key variables.

## 🗃️ Best Practices

- Keep `.envrc.link` in sync with your current configuration
- Always run `xo-fab env.status` before debugging issues
- Add project-specific logic in `.envrc.local` if needed

# Fabric Task Summary

- **`sync`**: 🔄 Sync pulses.
- **`archive-all`**: 🗃️ Archive all pulses.
- **`validate-tasks`**: 🔍 Validate import of all Fabric task modules in fab_tasks/
    Usage:
        fab validate_tasks
        fab validate_tasks:flags=--verbose
        fab validate_tasks:flags="--verbose --fail-on-error"
- **`summary`**: 📄 Show all registered Fabric tasks grouped by namespace.
    Arguments:
        to_md: Set to True to output in markdown format.
        filter_ns: Prefix filter for namespace, e.g., "vault." or "pulse."
        save_to: Optional file path to save markdown output.
- **`cz-lint`**: Run commitizen check, coverage badge, and static type checking.
- **`generate-completion`**: 🐚 Generate a bash-compatible tab-completion script for Fabric tasks.
- **`pulse.new`**: 📦 Create a new pulse entry.
- **`pulse.sync`**: 🔄 Sync pulses.
- **`pulse.archive-all`**: 🗃️ Archive all pulses.
- **`vault.sign`**: 
- **`vault.sign-all`**: 
- **`vault.verify-all`**: 
- **`vault.explorer-deploy`**: 
- **`vault.digest-generate`**: 
- **`vault.render-daily`**: 
- **`vault.publish-digest`**: 
- **`vault.unlock-memethic-path`**: 
- **`vault.archive-all`**: 
- **`collections.default`**: Default no-op task to satisfy Fabric validation.
- **`collections.summary`**: 📄 Show all registered Fabric tasks grouped by namespace.
- **`collections.ci.publish`**: 🚀 CI: Publish artifacts and log summary to Vault
- **`collections.vault.sign-all`**: 
- **`collections.vault.verify-all`**: 
- **`collections.pulse.sync`**: 🔄 Sync pulses.
- **`collections.core.core.validate-tasks`**: 🔍 Validate syntax of all Fabric task modules under fab_tasks/
- **`collections.validate.validate`**: 🔍 Validate import of all Fabric task modules in fab_tasks/
    Usage:
        fab validate_tasks
        fab validate_tasks:flags=--verbose
        fab validate_tasks:flags="--verbose --fail-on-error"
- **`drop.generate`**: Scaffold a new drop variant inside xo-drops.
- **`xo-agent.deploy-persona`**: Deploy a persona.
- **`xo-agent.reload-all`**: Reload all personas.
- **`xo-agent.list-personas`**: 
- **`xo-agent.test-dialog`**: 
- **`xo-agent.seed-personas-from-vault`**: 
- **`xo-agent.generate-mdx`**: 
- **`xo.deploy-persona`**: Deploy a persona.
- **`xo.reload-all`**: Reload all personas.
- **`xo.list-personas`**: 
- **`xo.test-dialog`**: 
- **`xo.seed-personas-from-vault`**: 
- **`xo.generate-mdx`**: 
- **`agent0.start`**: 🧠 Start Agent0 runtime
- **`agent0.generate-mdx`**: 
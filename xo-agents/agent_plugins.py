from shared.hooks.patch_hook import run_patch_hook

PLUGIN_HOOKS = {
    "patch": run_patch_hook,
    # add more plugins as needed
}

async def dispatch_persona(persona: str, payload: dict):
    plugin = payload.get("plugin")
    if plugin in PLUGIN_HOOKS:
        return PLUGIN_HOOKS[plugin](payload)
    return f"⚠️ No plugin found for: {plugin}"

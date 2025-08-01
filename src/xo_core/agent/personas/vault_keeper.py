from xo_core.agent.agent_hooks import AgentHooks


def ping_handler(payload):
    return {"reply": f"Vault Keeper received: {payload.get('test')}"}


def status_handler(payload):
    return {"status": "active", "role": "Vault Keeper"}


hooks = AgentHooks()
hooks.register("ping", ping_handler)
hooks.register("status", status_handler)

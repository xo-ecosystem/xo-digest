from xo_core.agent.agent_hooks import AgentHooks


def ping_handler(payload):
    return {"reply": f"Scribe logs ping: {payload.get('test')}"}


def status_handler(payload):
    return {"status": "ready", "role": "Scribe"}


hooks = AgentHooks()
hooks.register("ping", ping_handler)
hooks.register("status", status_handler)

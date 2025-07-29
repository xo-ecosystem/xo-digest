from invoke import task, Collection
from shared.agent_logic import dispatch_persona


@task
def dispatch_persona_cli(c, persona, webhook=False, preview=False, memory=False):
    """
    CLI task to dispatch a persona with optional webhook, preview, and memory support.
    """
    success = dispatch_persona(
        persona=persona,
        webhook=webhook,
        preview=preview,
        memory=memory,
    )
    if not success:
        raise Exception("Persona dispatch failed")


@task
def wire_hooks(c):
    """
    Wire the agent webhook and inbox plugin handlers.
    This is a placeholder for future automation of webhook and inbox dispatch logic.
    """
    print("🔌 Wiring Vault webhook → /run-task endpoint")
    print("📬 Wiring Inbox plugin → persona dispatch handler")


agent_ns = Collection("agent")
agent_ns.add_task(dispatch_persona_cli, "dispatch")
agent_ns.add_task(wire_hooks, "wire_hooks")

ns = Collection()
ns.add_collection(agent_ns)

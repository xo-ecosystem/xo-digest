from invoke import Collection, task


@task
def dispatch(c, persona=None, preview=False, webhook=False, memory=False):
    """
    CLI task to dispatch a persona with optional webhook, preview, and memory support.
    """
    from xo_core.agent.dispatch import dispatch_persona

    dispatch_persona(persona=persona, preview=preview, webhook=webhook, memory=memory)


@task
def wire_hooks(c):
    """
    Wire the agent webhook and inbox plugin handlers.
    """
    from xo_core.agent.hooks import wire_hooks

    wire_hooks()


from invoke import Collection

ns = Collection("agent")
ns.add_task(dispatch, "dispatch")
ns.add_task(wire_hooks, "wire-hooks")

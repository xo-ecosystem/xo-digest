from invoke import task
from xo_core.agent.persona import dispatch_persona


@task(
    help={
        "persona": "Name of the XO persona",
        "webhook": "Enable webhook forwarding",
        "preview": "Enable message previews",
        "memory": "Enable linked memory",
    }
)
def dispatch_persona_cli(ctx, persona, webhook=False, preview=False, memory=False):
    """
    CLI entrypoint for launching persona dispatcher
    Usage: fab dispatch.persona --persona=<name> [--webhook] [--preview] [--memory]
    """
    dispatch_persona(persona, webhook=webhook, preview=preview, memory=memory)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from invoke import task, Collection
import json
from pathlib import Path
from shared.agent_logic import dispatch_persona


def load_defaults():
    """Load default settings from .settings.json"""
    settings_path = Path(__file__).parent / "config" / "settings.json"
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}


@task(
    help={
        "persona": "Name of the XO persona",
        "webhook": "Enable webhook forwarding",
        "preview": "Enable message previews",
        "memory": "Enable linked memory",
    }
)
def dispatch_persona_cli(ctx, persona=None, webhook=False, preview=False, memory=False):
    """
    CLI entrypoint for launching persona dispatcher
    Usage: fab -f xo-agents/agent_cli.py dispatch_persona_cli --persona=<name> [--webhook] [--preview] [--memory]
    """
    defaults = load_defaults()
    persona = persona or defaults.get("persona", "default_persona")
    webhook = webhook or defaults.get("webhook", False)
    preview = preview or defaults.get("preview", False)
    memory = memory or defaults.get("memory", False)

    success = dispatch_persona(persona, webhook=webhook, preview=preview, memory=memory)

    if not success:
        print("❌ Persona dispatch failed")
        sys.exit(1)
    else:
        print("✅ Persona dispatch completed successfully")


@task
def list_personas(ctx):
    """List available personas"""
    personas_dir = Path(__file__).parent / "personas"
    if not personas_dir.exists():
        print("❌ No personas directory found")
        return

    print("📋 Available personas:")
    for persona_file in personas_dir.glob("*.py"):
        if persona_file.name != "__init__.py":
            persona_name = persona_file.stem
            print(f"  • {persona_name}")


# Create namespace and add tasks
ns = Collection()
ns.add_task(dispatch_persona_cli)
ns.add_task(list_personas)

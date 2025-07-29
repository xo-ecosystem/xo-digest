__all__ = ["dispatch_persona"]

import importlib
import importlib.util
import sys
from pathlib import Path


def dispatch_persona(persona, webhook=False, preview=False, memory=False):
    """
    Main dispatcher function that loads personas dynamically and executes plugin hooks

    Args:
        persona (str): Name of the persona to dispatch
        webhook (bool): Enable webhook forwarding
        preview (bool): Enable message previews
        memory (bool): Enable linked memory
    """
    print(f"🔁 Dispatching persona: {persona}")
    print(f"  • Webhook: {webhook}")
    print(f"  • Preview: {preview}")
    print(f"  • Memory: {memory}")

    # Always log the dispatch
    try:
        from shared.hooks import logger as logger_hook

        logger_hook.hook_logger(
            persona, webhook=webhook, preview=preview, memory=memory
        )
    except Exception as e:
        print(f"⚠️ Logger hook failed: {e}")

    # Load and run persona
    persona_content = None
    try:
        # Add xo-agents to path for persona imports
        xo_agents_path = Path(__file__).parent.parent / "xo-agents"
        if str(xo_agents_path) not in sys.path:
            sys.path.insert(0, str(xo_agents_path))

        # Try to import from personas
        persona_mod = importlib.import_module(f"personas.{persona}")
        persona_content = persona_mod.run()
    except ImportError:
        # Fallback to default persona
        try:
            persona_mod = importlib.import_module("personas.default_persona")
            print(f"❌ Could not load persona '{persona}', using default")
            persona_content = persona_mod.run()
        except Exception as e:
            print(f"❌ Could not load persona '{persona}' or default: {e}")
            return False

    # Execute plugin hooks
    if webhook:
        try:
            from shared.hooks import webhook as webhook_hook

            webhook_hook.hook_webhook(persona, payload={"content": persona_content})
        except Exception as e:
            print(f"⚠️ Webhook hook failed: {e}")

    if preview:
        try:
            from shared.hooks import preview as preview_hook

            preview_hook.hook_preview(persona, content=persona_content)
        except Exception as e:
            print(f"⚠️ Preview hook failed: {e}")

    if memory:
        try:
            from shared.hooks import memory as memory_hook

            memory_hook.hook_memory(
                persona,
                data={
                    "content": persona_content,
                    "hooks": {"webhook": webhook, "preview": preview},
                },
            )
        except Exception as e:
            print(f"⚠️ Memory hook failed: {e}")

    return True

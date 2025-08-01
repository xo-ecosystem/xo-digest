# Agent Persona Module
from fastapi import APIRouter, Request
from xo_core.agent.personas import persona_registry

router = APIRouter()


@router.post("/dispatch")
async def dispatch_persona(request: Request):
    data = await request.json()
    persona = data.get("persona", "vault_keeper")
    event = data.get("event", "ping")
    payload = data.get("payload", {})

    hooks = persona_registry.get(persona)
    if not hooks:
        return {"status": "error", "detail": f"Unknown persona '{persona}'"}

    response = hooks.trigger(event, payload)
    if response is None:
        return {"status": "error", "detail": f"No handler for event '{event}'"}

    return {"status": "ok", "persona": persona, "response": response}


class AgentPersona:
    def __init__(self, style: str = "neutral"):
        self.style = style

    def reply(self, message: str) -> str:
        if self.style == "cheerful":
            return f"😊 Yay! {message}"
        elif self.style == "serious":
            return f"🔍 Let's focus: {message}"
        elif self.style == "mystical":
            return f"🔮 The stars whisper: {message}"
        else:
            return f"{message}"

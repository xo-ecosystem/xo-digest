# Agent Core Dispatcher

from xo_core.agent.agent_persona import AgentPersona


def dispatch_persona(style: str, message: str) -> dict:
    persona = AgentPersona(style=style)
    reply = persona.reply(message)
    return {"style": style, "input": message, "reply": reply}

from fastapi import APIRouter, Request
from agent_plugins import dispatch_persona

router = APIRouter()

@router.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    persona = payload.get("persona", "vault_keeper")

    # Dispatch to agent (supports plugin hooks like "patch")
    result = await dispatch_persona(persona, payload)
    return {
        "status": "ok",
        "persona": persona,
        "result": result
    }

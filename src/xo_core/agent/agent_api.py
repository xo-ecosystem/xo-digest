from fastapi import APIRouter, Request
from xo_core.agent.agent_persona import router as persona_router
from xo_core.agent.agent_memory import router as memory_router

agent_api = APIRouter()

# ✅ Include persona and memory routers under /agent
agent_api.include_router(persona_router, prefix="/persona")
agent_api.include_router(memory_router, prefix="/memory")


@agent_api.get("/agent/echo")
async def echo_agent(request: Request):
    return {"msg": "Agent API is live", "headers": dict(request.headers)}

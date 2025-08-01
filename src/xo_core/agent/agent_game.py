# Agent Game Module
from fastapi import FastAPI
from xo_core.agent.agent_api import agent_api
from xo_core.agent.agent_memory import router as memory_router


class AgentGame:
    def __init__(self):
        self.app = FastAPI()

        self.app.include_router(agent_api, prefix="/agent")
        self.app.include_router(memory_router, prefix="/agent")

        @self.app.get("/health")
        def health_check():
            return {"status": "ok", "msg": "Agent system is alive"}

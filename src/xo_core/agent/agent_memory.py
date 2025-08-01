from fastapi import APIRouter
from xo_core.agent.memory.store import memory_store

router = APIRouter()


@router.get("/memory")
async def get_memory():
    return {"memory": memory_store}

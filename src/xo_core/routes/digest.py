from fastapi import APIRouter, Query
from pydantic import BaseModel

from xo_core.services.digest import publish_digest


router = APIRouter(tags=["digest"])


class DigestIn(BaseModel):
    title: str
    content: str


@router.post("/digest/publish")
def digest_publish(
    payload: DigestIn, fmt: str = Query("md", pattern="^(md|html|txt)$")
):
    publish_digest(payload.title, payload.content, fmt=fmt)
    return {"ok": True}

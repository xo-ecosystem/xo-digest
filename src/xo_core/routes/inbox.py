from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from typing import List
from pydantic import BaseModel

from xo_core.services.inbox import (
    add_message,
    list_messages,
    make_vault_inbox_url,
    make_vault_message_url,
)


router = APIRouter(tags=["inbox"])


class InboxMessage(BaseModel):
    sender: str
    content: str


@router.get("/inbox")
def inbox_list() -> List[dict]:
    return list_messages()


@router.post("/inbox")
def inbox_add(msg: InboxMessage):
    add_message(msg.dict())
    return {"ok": True}


@router.get("/inbox/{drop_id}")
def inbox_redirect(drop_id: str):
    url = make_vault_inbox_url(drop_id)
    if not url:
        raise HTTPException(status_code=404, detail="Unknown drop")
    return RedirectResponse(url)


@router.get("/inbox/{drop_id}/m/{mid}")
def inbox_message_redirect(drop_id: str, mid: str):
    url = make_vault_message_url(drop_id, mid)
    if not url:
        raise HTTPException(status_code=404, detail="Unknown message")
    return RedirectResponse(url)

from fastapi import APIRouter, Query, Request, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from xo_core.services.socials import get_social_feed
from xo_core.services.inbox import (
    get_latest_inbox_messages,
    make_vault_inbox_url,
    append_inbox_message,
)
from xo_core.rate_limit import get_tier_for_request
from xo_core.web.templates import templates

router = APIRouter(tags=["socials"])


class SocialFeed(BaseModel):
    drop: str
    messages: list
    view_all_url: str


@router.get("/socials/message_bottle")
def socials_message_bottle(
    request: Request, format: str = Query("json", enum=["json", "html", "markdown"])
):
    """
    Return latest social activity for the Message Bottle drop.
    Supports ?format=json|html|markdown.

    When format=json, response is tier-aware and returns a limited slice of inbox messages
    based on API key tier.
    """
    if format == "json":
        tier = get_tier_for_request(request)
        tier_limits = {
            "free": 5,
            "pro": 50,
            "ultra": 500,
        }
        limit = tier_limits.get(tier, 5)
        drop_id = "message_bottle"
        msgs = get_latest_inbox_messages(drop_id=drop_id, limit=limit)
        view_all_url = f"/inbox/{drop_id}"
        return {"drop": drop_id, "messages": msgs, "view_all_url": view_all_url}

    return get_social_feed(drop="message_bottle", format=format)


@router.get("/socials/message_bottle/page", include_in_schema=False)
def socials_message_bottle_page(request: Request):
    drop_id = "message_bottle"
    msgs = get_latest_inbox_messages(drop_id=drop_id, limit=20)
    view_all_url = f"/inbox/{drop_id}"
    return templates.TemplateResponse(
        "socials/message_bottle.html",
        {
            "request": request,
            "title": "XO • Message Bottle",
            "drop": drop_id,
            "messages": msgs,
            "view_all_url": view_all_url,
        },
    )


@router.post("/message-bottle/publish", include_in_schema=False)
def publish_message_bottle(user: str = Form(...), msg: str = Form(...)):
    drop_id = "message_bottle"
    append_inbox_message(drop_id, (user or "anon").strip(), (msg or "").strip())
    return RedirectResponse(url="/socials/message_bottle/page", status_code=303)

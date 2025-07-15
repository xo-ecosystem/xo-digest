from fastapi import APIRouter
from xo_core.fab_tasks.utils.digest_preview import render_all_digest_preview
from xo_core.fab_tasks.utils.digest_templates import digest_all_template
from xo_core.fab_tasks.utils.webhook_dispatch import trigger_digest_webhook

router = APIRouter()

@router.get("/vault/daily/preview/all")
async def full_digest_preview():
    html = digest_all_template()
    await trigger_digest_webhook(event="digest_preview", status="success", preview=True)
    return html
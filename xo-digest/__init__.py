

from fastapi import APIRouter, Request
from xo_digest.webhook.relay.handler import router as webhook_router

router = APIRouter()
router.include_router(webhook_router, prefix="/webhook")

def mount_routes(app):
    app.include_router(router)
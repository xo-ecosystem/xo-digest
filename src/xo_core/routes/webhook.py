from fastapi import APIRouter, Request
import logging, traceback

webhook_router = APIRouter()
log = logging.getLogger(__name__)


@webhook_router.post("/webhook-inbox")
async def webhook_inbox(request: Request):
    try:
        payload = await request.json()
        log.info(f"📥 Received webhook payload: {payload}")

        from xo_core.vault import process_payload as vault_process
        from xo_core.agent import dispatch_payload as agent_dispatch
        from xo_core.inbox import log_payload as inbox_log
        from xo_core.agent0 import dispatch_payload as agent0_dispatch
        from xo_core.agent1 import dispatch_payload as agent1_dispatch
        from xo_core.agent2 import dispatch_payload as agent2_dispatch
        from xo_core.agent3 import dispatch_payload as agent3_dispatch
        from xo_core.agent4 import dispatch_payload as agent4_dispatch
        from xo_core.pulse import dispatch_payload as pulse_dispatch
        from xo_core.preview import dispatch_payload as preview_dispatch

        vault_result = vault_process(payload)
        agent_result = agent_dispatch(payload)
        agent0_result = agent0_dispatch(payload)
        agent1_result = agent1_dispatch(payload)
        agent2_result = agent2_dispatch(payload)
        agent3_result = agent3_dispatch(payload)
        agent4_result = agent4_dispatch(payload)
        pulse_result = pulse_dispatch(payload)
        inbox_result = inbox_log(payload)
        preview_result = preview_dispatch(payload)

        return {
            "status": "received",
            "summary": "Payload routed to Vault, Agent0, and Inbox",
            "results": {
                "vault": vault_result,
                "agent": agent_result,
                "agent0": agent0_result,
                "agent1": agent1_result,
                "agent2": agent2_result,
                "agent3": agent3_result,
                "agent4": agent4_result,
                "pulse": pulse_result,
                "inbox": inbox_result,
                "preview": preview_result,
            },
        }
    except Exception as e:
        log.error(f"❌ Error in webhook_inbox: {e}")
        log.error(traceback.format_exc())
        return {"status": "error", "detail": str(e)}


@webhook_router.get("/agent/health")
async def health_check():
    return {"status": "ok", "msg": "Agent system is alive"}


@webhook_router.get("/agent/webhook")
async def agent_webhook():
    return {"msg": "Stub: Agent webhook endpoint (GET) not implemented"}

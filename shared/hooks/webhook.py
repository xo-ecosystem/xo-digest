import requests
import os


def hook_webhook(persona, payload=None):
    """Webhook plugin hook for persona dispatches"""
    url = os.getenv("XO_AGENT_WEBHOOK_URL")
    if not url:
        raise RuntimeError("XO_AGENT_WEBHOOK_URL is required but not set")
    message = {
        "persona": persona,
        "event": "dispatch_triggered",
        "payload": payload or {},
    }
    try:
        r = requests.post(url, json=message, timeout=4)
        print(f"📡 Webhook sent → {r.status_code}")
    except Exception as e:
        print(f"⚠️ Webhook failed: {e}")

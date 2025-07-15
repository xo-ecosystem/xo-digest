from invoke import Collection, task
from xo_core.vault.inbox_render import render_all_inbox_html

@task
def render(ctx):
    """Render all inbox messages to HTML"""
    html_output = render_all_inbox_html()
    print(html_output)
    
@task
def ping(c):
    print("📬 Inbox task module is active.")

@task
def notify_discord(c, message="📬 New inbox update from XO!"):
    import os
    import requests
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        return
    payload = {
        "embeds": [
            {
                "title": os.getenv("DISCORD_TITLE", "📬 XO Inbox Notification"),
                "description": message,
                "color": 5814783,
                "footer": {"text": "XO System"},
                "image": {"url": os.getenv("DISCORD_IMAGE_URL", "")}
            }
        ]
    }
    response = requests.post(webhook_url, json=payload)
    print(f"📨 Discord webhook response: {response.status_code}")

@task
def notify_telegram(c, message="📬 XO Inbox update via Telegram!"):
    import os
    import requests
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    thread_id = os.getenv("TELEGRAM_THREAD_ID")
    file_url = os.getenv("TELEGRAM_FILE_URL")
    if not token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        return

    headers = {"Content-Type": "application/json"}
    if file_url:
        endpoint = "sendPhoto" if file_url.lower().endswith((".png", ".jpg", ".jpeg")) else "sendDocument"
        url = f"https://api.telegram.org/bot{token}/{endpoint}"
        payload = {
            "chat_id": chat_id,
            "caption": message,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [[{"text": "Open XO", "url": os.getenv("XO_LINK_URL", "https://xo.to")}]]
            },
            "photo" if endpoint == "sendPhoto" else "document": file_url
        }
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [[{"text": "Open XO", "url": os.getenv("XO_LINK_URL", "https://xo.to")}]]
            }
        }

    if thread_id:
        payload["message_thread_id"] = int(thread_id)

    response = requests.post(url, headers=headers, json=payload)
    print(f"📨 Telegram bot response: {response.status_code}")
@task
def notify_all_with_link(c, message="📬 XO Update! [View more](https://xo.to)"):
    notify_discord(c, message)
    notify_telegram(c, message)

@task
def notify_all(c, message="📬 XO Inbox broadcast!"):
    notify_discord(c, message)
    notify_telegram(c, message)

ns = Collection("inbox")
notify_ns = Collection("notify")
notify_ns.add_task(notify_discord, name="discord")
notify_ns.add_task(notify_telegram, name="telegram")
notify_ns.add_task(notify_all, name="all")
notify_ns.add_task(notify_all_with_link, name="all_with_link")

ns.add_collection(notify_ns)
ns.add_task(ping, name="ping")
ns.add_task(render, name="render")

__all__ = ["ns"]
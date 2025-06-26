import os

import requests


def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    r = requests.post(url, data=data)
    print("Telegram:", r.status_code, r.text)


def send_discord(msg):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return
    data = {"content": msg}
    r = requests.post(webhook_url, json=data)
    print("Discord:", r.status_code, r.text)


if __name__ == "__main__":
    message = (
        "📬 *XO Vault Digest – 2025-06-23*\n\n"
        "🔗 [Link](https://xo-digest.pages.dev)\n"
        "📎 [Slim digest](https://xo-digest.pages.dev/vault/daily/2025-06-23.slim.md)\n"
        "🧬 Commit: `abcd123`\n"
        "⏱️ Duration: 17s"
    )
    send_telegram(message)
    send_discord(message)

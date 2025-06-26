# To schedule daily digest at midnight UTC:
# - GitHub Actions: use cron "0 0 * * *"
# - Local cron: `0 0 * * * python scripts/notify_webhook.py --daily-digest vault/logs --email`
import os
import smtplib
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def escape_markdown(text):
    return (
        text.replace("_", "\\_")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def get_git_info():
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
        return branch, commit
    except subprocess.SubprocessError:
        return "unknown", "unknown"


def send_email(subject, body, attachment_path=None):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("NOTIFY_EMAIL")
    pulse_url = os.getenv("PULSE_URL")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    success_count = os.getenv("CI_SUCCESS_COUNT", "1")

    if not all([smtp_server, smtp_user, smtp_pass, to_email]):
        print("⚠️ Email fallback skipped: SMTP credentials or target email missing.")
        return

    header_color = "#2ECC71" if success_count != "0" else "#E74C3C"

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    html_template = """
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
            .container {{
                padding: 20px;
                max-width: 600px;
                margin: auto;
                border: 1px solid #eee;
                border-radius: 8px;
                background-color: #f9f9f9;
            }}
            .header {{
                font-size: 18px;
                margin-bottom: 5px;
                color: {header_color};
            }}
            .date {{
                font-size: 12px;
                color: #666;
            }}
            .button {{
                display: inline-block;
                padding: 10px 16px;
                margin-top: 12px;
                font-size: 14px;
                background-color: #0d47a1;
                color: #fff;
                text-decoration: none;
                border-radius: 5px;
            }}
            .footer {{
                font-size: 12px;
                color: #888;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">📣 XO Notification</div>
            <div class="date">{today}</div>
            <div class="body">
                {body}
            </div>
            {pulse_link}
            <div class="footer">XO Core Automation System</div>
        </div>
    </body>
    </html>
    """.format(
        header_color=header_color,
        today=today,
        body=body,
        pulse_link=(
            f"<a class='button' href='{pulse_url}'>🔗 View Pulse</a>"
            if pulse_url
            else ""
        ),
    )

    msg.attach(MIMEText(html_template, "html"))

    if attachment_path and Path(attachment_path).exists():
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=Path(attachment_path).name)
            part["Content-Disposition"] = (
                f'attachment; filename="{Path(attachment_path).name}"'
            )
            msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            print("📧 Fallback email sent.")
    except Exception as e:
        print(f"❌ Failed to send fallback email: {e}")


def send_webhook(log_path, webhook_url, image_url=None, pulse_url=None):
    with open(log_path) as f:
        content = f.read()

    escaped_content = escape_markdown(content)
    branch, commit = get_git_info()
    duration = round(time.time() - send_webhook.start_time, 2)
    success_count = os.getenv("CI_SUCCESS_COUNT", "1")
    metrics = f"\n⏱ Duration: `{duration}` seconds\n✅ Successes: `{success_count}`"
    body = (
        f"📣 *XO CI Summary:*\n"
        f"_Branch_: `{branch}`\n"
        f"_Commit_: `{commit[:7]}`\n"
        f"```\n{escaped_content}\n```"
        f"{metrics}"
    )

    if pulse_url:
        body += f"\n🔗 [View Pulse]({pulse_url})"

    if "discord" in webhook_url:
        payload = {
            "content": None,
            "embeds": [
                {
                    "description": body.replace("*", "**").replace("`", ""),
                    "color": 3066993 if success_count != "0" else 15158332,
                    **({"image": {"url": image_url}} if image_url else {}),
                }
            ],
        }
    elif "telegram" in webhook_url:
        payload = {"text": body, "parse_mode": "MarkdownV2"}
        if image_url:
            payload["photo"] = image_url
    elif "slack.com" in webhook_url:
        payload = {
            "attachments": [
                {
                    "color": "#2ECC71" if success_count != "0" else "#E74C3C",
                    "blocks": [
                        {"type": "section", "text": {"type": "mrkdwn", "text": body}}
                    ],
                }
            ]
        }
    elif "matrix.org" in webhook_url or "/_matrix/" in webhook_url:
        payload = {
            "msgtype": "m.text",
            "body": body.replace("*", "").replace("`", ""),
        }
    else:
        payload = {"text": body}

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"✅ Webhook sent successfully: {response.status_code}")
        # Optionally add: fallback email handler if webhook fails
    except requests.RequestException as e:
        print(f"❌ Failed to send webhook: {e}")
        subject = "XO Webhook Delivery Failed"
        send_email(subject, body.replace("\n", "<br>"), attachment_path=log_path)


def send_daily_digest(logs_dir, webhook_urls, email=False):
    digest = defaultdict(list)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    for log_file in sorted(Path(logs_dir).glob("*.log")):
        if (
            datetime.utcfromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d")
            != today
        ):
            continue
        with open(log_file) as f:
            digest[log_file.name].append(f.read())

    full_report = f"📅 *XO Daily CI Digest: {today}*\n"
    for name, entries in digest.items():
        summary_lines = "".join(entries).strip().splitlines()
        summary = f"{len(summary_lines)} lines"
        full_report += (
            f"\n🔹 `{name}` ({summary})\n```\n{''.join(entries).strip()}\n```"
        )

    summary_path = Path(logs_dir) / f"daily_digest_{today}.log"
    summary_path.write_text(full_report)

    for url in webhook_urls:
        send_webhook(str(summary_path), url)

    if email:
        send_email(
            f"XO Daily Digest - {today}",
            full_report.replace("```", "<br>").replace("\n", "<br>"),
            attachment_path=str(summary_path),
        )


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send XO CI webhook")
    parser.add_argument("log_path", help="Path to the summary log file")
    parser.add_argument(
        "--test", action="store_true", help="Preview payload without sending"
    )
    parser.add_argument(
        "--daily-digest",
        metavar="LOGS_DIR",
        help="Send grouped digest from this logs directory",
    )
    parser.add_argument(
        "--email", action="store_true", help="Also send via fallback email"
    )
    args = parser.parse_args()

    webhook_urls = [
        url.strip() for url in os.getenv("WEBHOOK_URL", "").split(",") if url.strip()
    ]

    if args.daily_digest:
        send_daily_digest(args.daily_digest, webhook_urls, email=args.email)
        sys.exit(0)

    if not webhook_urls:
        print("❌ No WEBHOOK_URL values found in .env")
        sys.exit(1)

    image_url = os.getenv("WEBHOOK_IMAGE")
    if not image_url:
        image_url = "https://xodrops.com/static/xo_default_banner.jpg"
    pulse_url = os.getenv("PULSE_URL")

    with open(args.log_path) as f:
        content = f.read()

    escaped_content = escape_markdown(content)
    branch, commit = get_git_info()

    start_time = time.time()
    send_webhook.start_time = start_time

    for url in webhook_urls:
        if args.test:
            duration = round(time.time() - start_time, 2)
            success_count = os.getenv("CI_SUCCESS_COUNT", "1")
            metrics = (
                f"\n⏱ Duration: `{duration}` seconds\n✅ Successes: `{success_count}`"
            )
            payload_body = (
                f"📣 *XO CI Summary:*\n"
                f"_Branch_: `{branch}`\n"
                f"_Commit_: `{commit[:7]}`\n"
                f"```\n{escaped_content}\n```"
                f"{metrics}"
            )
            payload = {"text": payload_body, "parse_mode": "MarkdownV2"}
            print(f"🧪 TEST MODE ({url}):")
            print(payload)
        else:
            send_webhook(args.log_path, url, image_url=image_url, pulse_url=pulse_url)

    duration = round(time.time() - start_time, 2)
    success_count = os.getenv("CI_SUCCESS_COUNT", "1")
    metrics = f"\n⏱ Duration: `{duration}` seconds\n✅ Successes: `{success_count}`"

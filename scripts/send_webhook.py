#!/usr/bin/env python3
import argparse
import json
import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import requests


def print_summary(args):
    print("\n📡 Webhook Summary:")
    print(f"  🔧 Event: {args.event}")
    print(f"  📌 Status: {args.status.upper()}")
    if args.link:
        print(f"  🔗 Link: {args.link}")
    if args.sha:
        print(f"  🧬 Commit SHA: {args.sha}")
    if args.duration:
        print(f"  ⏱️ Duration: {args.duration} seconds")
    if args.excerpt:
        print(f"  📝 Excerpt: {args.excerpt}")
    if args.attach:
        for path in args.attach:
            exists = Path(path).exists()
            print(f"  📎 Attachment: {path} {'✅' if exists else '❌'}")


def find_latest_note_excerpt():
    vault_path = Path("vault/daily")
    if not vault_path.exists() or not vault_path.is_dir():
        return None
    md_files = list(vault_path.glob("*.md")) + list(vault_path.glob("*.mdx"))
    if not md_files:
        return None
    latest_file = max(md_files, key=lambda f: f.stat().st_mtime)
    try:
        with latest_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    # Remove leading '#' and whitespace
                    return line.lstrip("#").strip()
    except Exception:
        return None
    return None


def create_zip_attachment(paths):
    temp_dir = tempfile.mkdtemp()
    zip_path = Path(temp_dir) / "attachments.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for p in paths:
            p_path = Path(p)
            if p_path.exists() and p_path.is_file():
                zipf.write(p_path, arcname=p_path.name)
    return zip_path


def send_discord_webhook(url, content, files=None):
    data = {"content": content}
    if files:
        with open(files, "rb") as f:
            file_data = {"file": (files.name, f)}
            response = requests.post(url, data=data, files=file_data)
    else:
        response = requests.post(url, json=data)
    if response.status_code >= 400:
        print(
            f"Discord webhook failed with status {response.status_code}: {response.text}",
            file=sys.stderr,
        )


def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "MarkdownV2"}
    response = requests.post(url, json=payload)
    if response.status_code >= 400:
        print(
            f"Telegram message failed with status {response.status_code}: {response.text}",
            file=sys.stderr,
        )


def format_markdown_block(args):
    lines = []
    lines.append(f"**Event:** {args.event}")
    lines.append(f"**Status:** {args.status.upper()}")
    if args.link:
        lines.append(f"**Link:** [Link]({args.link})")
    if args.sha:
        lines.append(f"**Commit SHA:** `{args.sha}`")
    if args.duration:
        lines.append(f"**Duration:** {args.duration} seconds")
    if args.excerpt:
        # Escape backticks and backslashes for MarkdownV2
        safe_excerpt = (
            args.excerpt.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("_", "\\_")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("(", "\\(")
            .replace(")", "\\)")
            .replace("~", "\\~")
            .replace(">", "\\>")
            .replace("#", "\\#")
            .replace("+", "\\+")
            .replace("-", "\\-")
            .replace("=", "\\=")
            .replace("|", "\\|")
            .replace("{", "\\{")
            .replace("}", "\\}")
            .replace(".", "\\.")
            .replace("!", "\\!")
        )
        lines.append(f"**Excerpt:**\n```\n{safe_excerpt}\n```")
    if args.attach:
        for path in args.attach:
            lines.append(f"📎 Attachment: `{path}`")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Simulate webhook payload for testing."
    )
    parser.add_argument(
        "--event", required=True, help="Event name (e.g., digest_publish)"
    )
    parser.add_argument(
        "--status", required=True, choices=["success", "fail"], help="Status of the job"
    )
    parser.add_argument("--link", help="Link to include in the notification")
    parser.add_argument("--sha", help="Commit SHA")
    parser.add_argument("--duration", type=int, help="Job duration in seconds")
    parser.add_argument("--excerpt", help="Log or digest excerpt")
    parser.add_argument(
        "--attach", nargs="*", help="Paths to files to attach (optional)"
    )
    args = parser.parse_args()

    # If excerpt not provided, try to auto-parse latest note
    if not args.excerpt:
        args.excerpt = find_latest_note_excerpt()

    # Validate attachments
    valid_attachments = []
    if args.attach:
        for p in args.attach:
            if Path(p).exists():
                valid_attachments.append(p)
    args.attach = valid_attachments if valid_attachments else None

    print_summary(args)

    # Prepare message content
    message = format_markdown_block(args)

    discord_url = os.environ.get("DISCORD_WEBHOOK_URL")
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # Send webhook or fallback to logging
    if discord_url or (telegram_token and telegram_chat_id):
        # Handle attachments: if more than one, bundle into zip
        zip_file = None
        if args.attach and len(args.attach) > 1:
            zip_file = create_zip_attachment(args.attach)
        try:
            if discord_url:
                if zip_file:
                    send_discord_webhook(discord_url, message, files=zip_file)
                else:
                    send_discord_webhook(discord_url, message)
            if telegram_token and telegram_chat_id:
                # Telegram does not support file uploads here, so just send message
                send_telegram_message(telegram_token, telegram_chat_id, message)
        finally:
            if zip_file and zip_file.exists():
                try:
                    zip_file.unlink()
                    zip_file.parent.rmdir()
                except Exception:
                    pass
    else:
        # Fallback logging for CI or xo-fab use
        print("\n⚠️ No webhook credentials found. Logging message instead:\n")
        print(message)


if __name__ == "__main__":
    main()

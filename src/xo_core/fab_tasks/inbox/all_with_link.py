# Optional env vars:
# TELEGRAM_REPLY_TO_MESSAGE_ID – used to thread messages
# DISCORD_THREAD_ID – optional, for Discord webhook thread (not implemented yet)
# TELEGRAM_PHOTO_URL – to attach a photo
# TELEGRAM_VIDEO_URL – to attach a video
# TELEGRAM_INLINE_BUTTONS_JSON – to attach inline buttons (JSON-encoded)

from invoke import task
import os
import json
import requests

# Attempt to import markdown2, warn and skip if not available
try:
    import markdown2
except ImportError:
    print("⚠️ Skipping inbox.all_with_link: 'markdown2' module not found.")
    markdown2 = None

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


@task
def all_with_link(c, link="https://xo.to/", message="🔗 XO Drop available!", markdown=True):
    """
    Send enriched inbox notification with a link.
    """

    # If markdown2 is not available, warn and skip this task to avoid crashing xo-fab
    if markdown2 is None:
        print("⚠️ inbox.all_with_link: 'markdown2' module is not installed. Skipping task.")
        return

    # Convert Markdown to HTML for richer previews
    message_html = markdown2.markdown(message) if markdown else message

    # Ensure markdown is available for Discord block
    # (markdown param is already above)

    if DISCORD_WEBHOOK_URL:
        discord_data = {
            "content": message,
            "embeds": [
                {
                    "title": "📬 XO Inbox Link",
                    "description": markdown2.markdown(message) if markdown else message,
                    "url": link,
                    "color": 16742840,
                }
            ]
        }
        if not markdown:
            discord_data["embeds"][0]["description"] = f"{message}\n{link}"
        # Optional: attach file to Discord
        discord_file_url = os.getenv("DISCORD_FILE_URL")
        if discord_file_url:
            discord_file_data = {
                "content": message,
            }
            discord_file_files = {
                "file": requests.get(discord_file_url, stream=True).raw
            }
            try:
                requests.post(DISCORD_WEBHOOK_URL, data=discord_file_data, files=discord_file_files)
            except Exception as e:
                print(f"⚠️ Discord file upload failed: {e}")

        requests.post(DISCORD_WEBHOOK_URL, json=discord_data)
        # Optionally mirror to a second Discord webhook
        discord_mirror_url = os.getenv("DISCORD_EMBED_MIRROR_URL")
        if discord_mirror_url:
            try:
                requests.post(discord_mirror_url, json=discord_data)
            except Exception as e:
                print(f"⚠️ Discord embed mirror failed: {e}")

        # Optional: Discord reaction-based routing logic hint
        discord_reaction_routing = os.getenv("DISCORD_REACTION_ROUTING")
        if discord_reaction_routing:
            try:
                routing = json.loads(discord_reaction_routing)
                print(f"⚙️ Reaction-based routing defined. Example:")
                for emoji, action in routing.items():
                    print(f"  {emoji} → {action}")
            except Exception as e:
                print(f"⚠️ Invalid reaction routing config: {e}")

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        text = f"<b>{message}</b>\n<a href=\"{link}\">📎 View drop</a>" if markdown else f"{message}\n{link}"
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        telegram_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML" if markdown else None,
            "disable_web_page_preview": False,
        }

        # Optional: reply to a specific message to create a thread
        thread_id = os.getenv("TELEGRAM_REPLY_TO_MESSAGE_ID")

        digest_thread_hint = os.getenv("DIGEST_THREAD_ID")
        if not thread_id and digest_thread_hint:
            telegram_payload["reply_to_message_id"] = int(digest_thread_hint)
        elif thread_id:
            telegram_payload["reply_to_message_id"] = int(thread_id)

        # Optional: attach media (photo)
        media_url = os.getenv("TELEGRAM_PHOTO_URL")
        if media_url:
            telegram_photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            telegram_photo_payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": media_url,
                "caption": message_html if markdown else message,
                "parse_mode": "HTML" if markdown else None,
            }
            requests.post(telegram_photo_url, json=telegram_photo_payload)

        # Optional: attach media (video)
        video_url = os.getenv("TELEGRAM_VIDEO_URL")
        if video_url:
            telegram_video_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
            telegram_video_payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "video": video_url,
                "caption": message_html if markdown else message,
                "parse_mode": "HTML" if markdown else None,
            }
            requests.post(telegram_video_url, json=telegram_video_payload)

        # Optional: auto-detect video or file from MESSAGE_CONTENT_TYPE
        content_type = os.getenv("MESSAGE_CONTENT_TYPE")
        content_url = os.getenv("MESSAGE_CONTENT_URL")
        if content_type and content_url:
            if content_type == "video":
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "video": content_url,
                    "caption": message_html if markdown else message,
                    "parse_mode": "HTML" if markdown else None,
                })
            elif content_type == "document":
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "document": content_url,
                    "caption": message_html if markdown else message,
                    "parse_mode": "HTML" if markdown else None,
                })

        # Optional: media carousel
        album_json = os.getenv("TELEGRAM_MEDIA_ALBUM_JSON")
        if album_json:
            try:
                media_group = json.loads(album_json)
                # Append link as caption if missing
                for item in media_group:
                    if "caption" not in item or not item["caption"]:
                        item["caption"] = f"<a href='{link}'>📎 View drop</a>"
                    if "parse_mode" not in item:
                        item["parse_mode"] = "HTML" if markdown else None
                telegram_media_group_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMediaGroup"
                album_payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "media": media_group
                }
                requests.post(telegram_media_group_url, json=album_payload)
            except Exception as e:
                print(f"⚠️ Failed to send media album: {e}")

        # Optional: auto-generate media album from semicolon-separated list
        media_album_urls = os.getenv("TELEGRAM_MEDIA_ALBUM_URLS")
        if media_album_urls:
            try:
                urls = media_album_urls.split(";")
                media_group = []
                for url in urls:
                    url = url.strip()
                    if url:
                        media_group.append({
                            "type": "photo",
                            "media": url,
                            "caption": f"<a href='{link}'>📎 View drop</a>",
                            "parse_mode": "HTML" if markdown else None
                        })
                if media_group:
                    telegram_media_group_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMediaGroup"
                    album_payload = {
                        "chat_id": TELEGRAM_CHAT_ID,
                        "media": media_group
                    }
                    requests.post(telegram_media_group_url, json=album_payload)
            except Exception as e:
                print(f"⚠️ Failed to auto-generate media album: {e}")

        # Optional: inline keyboard buttons
        buttons_json = os.getenv("TELEGRAM_INLINE_BUTTONS_JSON")
        if buttons_json:
            try:
                buttons = json.loads(buttons_json)
                if isinstance(buttons[0], dict):
                    # Wrap single row buttons in list
                    buttons = [buttons]
                telegram_payload.setdefault("reply_markup", {})["inline_keyboard"] = buttons
            except Exception as e:
                print(f"⚠️ Failed to parse TELEGRAM_INLINE_BUTTONS_JSON: {e}")
            else:
                if not buttons:
                    telegram_payload.setdefault("reply_markup", {})["inline_keyboard"] = [[
                        {"text": "📎 View", "url": link}
                    ]]

        # Optional: attach file/document
        file_url = os.getenv("TELEGRAM_FILE_URL")
        if file_url:
            telegram_doc_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            telegram_doc_payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "document": file_url,
                "caption": message_html if markdown else message,
                "parse_mode": "HTML" if markdown else None,
            }
            requests.post(telegram_doc_url, json=telegram_doc_payload)

        requests.post(telegram_url, json=telegram_payload)

        # Optional: HTML preview fallback if Markdown is disabled
        if not markdown:
            html_preview_url = os.getenv("TELEGRAM_HTML_PREVIEW_URL")
            if html_preview_url:
                telegram_html_payload = {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": f"<a href='{html_preview_url}'>🖼️ View HTML preview</a>",
                    "parse_mode": "HTML"
                }
                requests.post(telegram_url, json=telegram_html_payload)

        if DISCORD_WEBHOOK_URL:
            mirror_text = f"📬 Mirrored Telegram: {message}"
            requests.post(DISCORD_WEBHOOK_URL, json={"content": mirror_text})

    digest_thread_hint = os.getenv("DIGEST_THREAD_ID")
    if digest_thread_hint:
        print(f"🧵 Digest thread scaffold active. Reply chain can follow-up with ID: {digest_thread_hint}")

    # Optional: Markdown-to-HTML visual preview
    html_preview = os.getenv("HTML_PREVIEW_OUTPUT_PATH")
    if html_preview:
        try:
            html_content = markdown2.markdown(message)
            with open(html_preview, "w") as f:
                f.write(f"<html><body>{html_content}</body></html>")
            print(f"🖼️ Markdown preview rendered to: {html_preview}")
            # --- Auto-upload to IPFS and attach to Discord/Telegram ---
            ipfs_api_key = os.getenv("NFT_STORAGE_API_KEY")
            if ipfs_api_key:
                try:
                    import base64
                    with open(html_preview, "rb") as f:
                        preview_data = f.read()
                    upload_response = requests.post(
                        "https://api.nft.storage/upload",
                        headers={"Authorization": f"Bearer {ipfs_api_key}"},
                        files={"file": ("preview.html", preview_data, "text/html")}
                    )
                    if upload_response.ok:
                        ipfs_url = upload_response.json()["value"]["cid"]
                        html_cid_url = f"https://ipfs.io/ipfs/{ipfs_url}"
                        print(f"📎 IPFS uploaded preview: {html_cid_url}")
                        # Attach to Telegram
                        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                        telegram_preview_payload = {
                            "chat_id": TELEGRAM_CHAT_ID,
                            "text": f"<a href='{html_cid_url}'>🖼️ IPFS HTML preview</a>",
                            "parse_mode": "HTML"
                        }
                        requests.post(telegram_url, json=telegram_preview_payload)
                        # Attach to Discord
                        discord_embed_attachment = {
                            "embeds": [{
                                "title": "🖼️ IPFS HTML Preview",
                                "url": html_cid_url,
                                "description": "View the styled Markdown preview on IPFS",
                                "color": 16742840
                            }]
                        }
                        requests.post(DISCORD_WEBHOOK_URL, json=discord_embed_attachment)
                    else:
                        print(f"⚠️ Failed IPFS upload: {upload_response.status_code}")
                except Exception as e:
                    print(f"⚠️ Error uploading HTML preview to IPFS: {e}")
            # --- End IPFS auto-upload ---
        except Exception as e:
            print(f"⚠️ Failed to render Markdown preview: {e}")

    print(f"✅ Sent message to inbox channels with link: {link}")

    # Optional: extract summary from .mdx file if path provided
    ai_summary = os.getenv("AI_DIGEST_SUMMARY")
    mdx_path = os.getenv("MDX_SOURCE_PATH")
    if mdx_path and not ai_summary:
        try:
            with open(mdx_path, "r") as f:
                lines = f.readlines()
            for line in lines:
                if line.strip().startswith("summary:") or line.strip().startswith("summary ="):
                    ai_summary = line.split(":", 1)[1].strip() if ":" in line else line.split("=", 1)[1].strip()
                    print(f"🧠 Extracted summary from .mdx: {ai_summary}")
                    break
        except Exception as e:
            print(f"⚠️ Failed to read summary from .mdx file: {e}")

    # 🧠 AI-generated reply hook (placeholder)
    if ai_summary:
        print(f"🧠 AI Summary: {ai_summary}")
        # Optionally send it as threaded reply or separate message
        summary_payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": f"<b>🧠 Summary:</b>\n{ai_summary}",
            "parse_mode": "HTML",
        }
        if digest_thread_hint:
            summary_payload["reply_to_message_id"] = int(digest_thread_hint)
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json=summary_payload)

        # Mirror AI summary to Discord
        discord_ai_embed = {
            "embeds": [{
                "title": "🧠 AI Digest Summary",
                "description": ai_summary,
                "color": 16742840
            }]
        }
        if DISCORD_WEBHOOK_URL:
            requests.post(DISCORD_WEBHOOK_URL, json=discord_ai_embed)

    # 📎 Auto-pinning support for Telegram
    auto_pin = os.getenv("TELEGRAM_AUTO_PIN") == "1"
    if auto_pin and 'message_id' in locals().get('telegram_payload', {}):
        try:
            pin_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/pinChatMessage"
            requests.post(pin_url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "message_id": telegram_payload.get("reply_to_message_id"),
                "disable_notification": True
            })
            print("📌 Auto-pinned Telegram message.")
        except Exception as e:
            print(f"⚠️ Failed to auto-pin Telegram message: {e}")

    # 🎛️ Dynamic inline keyboard behavior via JSON or fallback
    fallback_buttons = os.getenv("FALLBACK_INLINE_BUTTONS")
    if fallback_buttons and not locals().get('buttons_json'):
        try:
            fallback = json.loads(fallback_buttons)
            telegram_payload.setdefault("reply_markup", {})["inline_keyboard"] = fallback
        except Exception as e:
            print(f"⚠️ Failed to parse FALLBACK_INLINE_BUTTONS: {e}")

from invoke import Collection

def get_ns():
    ns = Collection("all_with_link")
    ns.add_task(all_with_link, name="all_with_link")
    return ns
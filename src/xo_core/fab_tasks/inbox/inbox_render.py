__package__ = "xo_core.vault"

__all__ = ["render_all_inbox_html", "render_all_inbox_to_html"]

import os
import re
from pathlib import Path
import markdown
import yaml

def render_all_inbox_html() -> str:
    inbox_dir = Path("vault/.inbox")
    if not inbox_dir.exists():
        return "<section id='inbox-preview'><p>No inbox directory found.</p></section>"

    messages = []
    for file_path in inbox_dir.glob("*.mdx"):
        if file_path.stat().st_size == 0:
            continue
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split YAML frontmatter and body
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    meta_yaml, body = parts[1], parts[2]
                    meta = yaml.safe_load(meta_yaml)
                else:
                    meta = {}
                    body = content
            else:
                meta = {}
                body = content

            title = meta.get("title", "Untitled")
            date = meta.get("date", "Unknown Date")
            manifest = meta.get("manifest", "Unknown Manifest")

            html_content = markdown.markdown(
                body,
                extensions=["codehilite", "tables", "toc", "fenced_code", "nl2br"],
            )

            # Enhance IPFS and Arweave links
            html_content = re.sub(
                r"\b(Qm[a-zA-Z0-9]{44,})\b",
                r'<a href="https://ipfs.io/ipfs/\1">\1</a>',
                html_content,
            )
            html_content = re.sub(
                r"\b([a-zA-Z0-9_-]{43})\b",
                r'<a href="https://arweave.net/\1">\1</a>',
                html_content,
            )

            message_html = f"""
            <div class="inbox-message" style="border:1px solid #ddd; padding:1em; margin-bottom:1em;">
                <div class="inbox-header" style="font-weight:bold;">
                    {title} <small style="float:right;">{date}</small>
                </div>
                <div class="inbox-meta" style="color: #777; font-size: 0.9em;">
                    Manifest: {manifest}
                </div>
                <div class="inbox-body">
                    {html_content}
                </div>
                <div class="inbox-footer" style="margin-top:1em;">
                    <small><em>Source: {file_path.name}</em></small>
                </div>
            </div>
            """
            messages.append(message_html)
        except Exception as e:
            messages.append(f"<div class='inbox-message error'>Error loading {file_path.name}: {str(e)}</div>")

    if not messages:
        return "<section id='inbox-preview'><p>No messages in inbox.</p></section>"

    combined_html = "<section id='inbox-preview'>" + "\n".join(messages) + "</section>"
    return combined_html


render_all_inbox_to_html = render_all_inbox_html
from typing import Literal
import html as _html

from xo_core.services.inbox import get_messages


def get_social_feed(drop: str, format: Literal["json", "html", "markdown"] = "json"):
    """
    Get a social feed for a given drop.
    Supports json, html, and markdown output.
    """
    all_msgs = get_messages()
    filtered = [m for m in all_msgs if m.get("meta", {}).get("drop") == drop]

    if format == "json":
        return {
            "drop": drop,
            "count": len(filtered),
            "messages": filtered,
        }

    if format == "html":
        html_msgs = []
        for m in filtered:
            user = _html.escape(m.get("user", m.get("sender", "anon")))
            text = _html.escape(m.get("text", m.get("content", "")))
            html_msgs.append(f"<div class='msg'><b>{user}</b>: {text}</div>")
        return "\n".join(html_msgs)

    if format == "markdown":
        md_msgs = []
        for m in filtered:
            user = m.get("user", m.get("sender", "anon"))
            text = m.get("text", m.get("content", ""))
            md_msgs.append(f"- **{user}**: {text}")
        return "\n".join(md_msgs)

    raise ValueError(f"Unsupported format: {format}")

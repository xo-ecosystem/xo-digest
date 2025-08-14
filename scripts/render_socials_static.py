#!/usr/bin/env python3
"""
Render a static HTML page for the Message Bottle social feed.
Writes to public/socials/message_bottle.html

Usage:
  python scripts/render_socials_static.py
"""
from pathlib import Path
from datetime import datetime, timezone

# Reuse the existing socials feed service
from xo_core.services.socials import get_social_feed

OUT_DIR = Path("public/socials")
OUT_FILE = OUT_DIR / "message_bottle.html"

BASE_CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { margin: 0; font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, system-ui, Arial, sans-serif; }
.wrap { max-width: 820px; margin: 0 auto; padding: 24px; }
.header { display:flex; align-items:center; gap:12px; }
.badge { padding: 2px 8px; border-radius: 999px; font-size:12px; border:1px solid #9994; }
.hint { color: #666; font-size: 13px; }
.msg { padding: 10px 0; border-bottom: 1px dashed #9993; }
.msg:last-child { border-bottom: 0; }
.user { font-weight: 600; }
.footer { margin-top: 20px; color:#666; font-size: 12px; }
a { color: inherit; }
.time { font-variant-numeric: tabular-nums; }
"""

HTML_SHELL = """<!doctype html>
<html lang=\"en\">
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>XO Socials · Message Bottle</title>
<meta name=\"robots\" content=\"index,follow\">
<style>{css}</style>
<body>
  <div class=\"wrap\">
    <div class=\"header\">
      <h1 style=\"margin:0\">Message Bottle</h1>
      <span class=\"badge\">Live Socials</span>
    </div>
    <p class=\"hint\">Auto-generated static snapshot. Latest messages inline.</p>
    <div id=\"feed\">
{feed_html}
    </div>
    <div class=\"footer\">
      <div>Built: <span class=\"time\">{built_at}</span> UTC</div>
      <div>Drop: message_bottle · Count: {count}</div>
    </div>
  </div>
</body>
</html>
"""


def indent_block(s: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in s.splitlines())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Get the already-escaped HTML block from our service:
    feed_html = get_social_feed(drop="message_bottle", format="html") or ""
    # Count via json helper to avoid parsing HTML
    meta = get_social_feed(drop="message_bottle", format="json")
    count = meta.get("count", 0) if isinstance(meta, dict) else 0

    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    html = HTML_SHELL.format(
        css=BASE_CSS,
        feed_html=indent_block(feed_html, spaces=6),
        built_at=built_at,
        count=count,
    )
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"✔ Wrote {OUT_FILE} (messages={count})")


if __name__ == "__main__":
    main()

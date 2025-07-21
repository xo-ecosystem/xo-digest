from pathlib import Path
from jinja2 import Template
from xo_core.vault.ipfs_utils import log_status

PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>{{ title }}</title>
    <style>
      body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 720px; margin: auto; background: #f8f9fa; }
      h1 { color: #111; }
      pre, code { background: #eee; padding: 0.2rem 0.5rem; border-radius: 4px; }
      .meta { margin-top: 1rem; font-size: 0.9rem; color: #555; }
      .content { margin-top: 2rem; }
    </style>
  </head>
  <body>
    <h1>{{ title }}</h1>
    <div class="meta">
      {% if ipfs_hash %}<p>📦 IPFS Hash: <code>{{ ipfs_hash }}</code></p>{% endif %}
      {% if slug %}<p>🔖 Slug: <code>{{ slug }}</code></p>{% endif %}
      {% if date %}<p>📅 Date: <code>{{ date }}</code></p>{% endif %}
    </div>
    <div class="content">
      {{ content | safe }}
    </div>
  </body>
</html>
"""

def render_signed_preview(pulse, output_path):
    try:
        template = Template(PREVIEW_TEMPLATE)
        html = template.render(
            title=pulse.get("title", "Untitled"),
            slug=pulse.get("slug"),
            date=pulse.get("metadata", {}).get("date"),
            content=pulse.get("content", ""),
            ipfs_hash=pulse.get("ipfs_hash", "unknown")
        )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        log_status(f"📄 [bold green]Preview saved:[/bold green] {output_path}", level="success")
    except Exception as e:
        log_status(f"🚫 [red]Render error for {pulse.get('slug')}[/red]: {str(e)}", level="error")
from pathlib import Path
import markdown
from fastapi.responses import HTMLResponse
import yaml

def render_mdx_preview(mdx_path: Path) -> HTMLResponse:
    """
    Renders an .mdx file as HTML for inbox preview use.
    """
    if not mdx_path.exists():
        return HTMLResponse(content="⚠️ File not found", status_code=404)
    md_text = mdx_path.read_text()

    persona_slug = "seal_dream"
    persona_name = "Seal Dream"
    persona_meta = mdx_path.with_suffix(".persona.yml")
    if persona_meta.exists():
        with open(persona_meta, "r") as f:
            try:
                meta = yaml.safe_load(f)
                persona_slug = meta.get("slug", persona_slug)
                persona_name = meta.get("name", persona_name)
            except Exception as e:
                print(f"⚠️ Failed to load persona metadata: {e}")

        persona_avatar = f"/static/personas/{persona_slug}.png"
        if meta.get("avatar"):
            persona_avatar = meta["avatar"]

    html_body = markdown.markdown(md_text, extensions=["extra", "tables", "sane_lists"])
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inbox Preview</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;700&display=swap');

            body {{
                animation: fadeIn 0.6s ease-out;
                font-family: 'Fira Sans', sans-serif;
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}

            .persona-avatar {{
                border-radius: 50%;
                width: 64px;
                height: 64px;
                object-fit: cover;
                margin-right: 0.5em;
                vertical-align: middle;
            }}

            :root {{
                --bg-color: #0f1117;
                --text-color: #e0e6ed;
                --link-color: #88ccff;
                --header-color: #ffffff;
                --table-border: #3a3f4b;
                --table-header-bg: #1a1d26;
                --table-row-even: #1e212b;
                --code-bg: #262b36;
            }}
            body.light {{
                --bg-color: #ffffff;
                --text-color: #000000;
                --link-color: #007acc;
                --header-color: #111111;
                --table-border: #cccccc;
                --table-header-bg: #f0f0f0;
                --table-row-even: #fafafa;
                --code-bg: #f4f4f4;
            }}
            body {{
                font-family: "Segoe UI", Roboto, sans-serif;
                margin: 2em;
                background-color: var(--bg-color);
                color: var(--text-color);
            }}
            a {{
                color: var(--link-color);
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: var(--header-color);
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 1em;
            }}
            th, td {{
                border: 1px solid var(--table-border);
                padding: 0.75em;
            }}
            th {{
                background: var(--table-header-bg);
                color: var(--header-color);
            }}
            tr:nth-child(even) {{
                background-color: var(--table-row-even);
            }}
            code {{
                background-color: var(--code-bg);
                padding: 0.2em 0.4em;
                border-radius: 4px;
                font-family: "Courier New", monospace;
            }}
            pre {{
                background-color: var(--code-bg);
                padding: 1em;
                border-radius: 4px;
                overflow-x: auto;
            }}
            #theme-toggle {{
                position: fixed;
                top: 1em;
                right: 1em;
                padding: 0.5em 1em;
                background: var(--table-header-bg);
                color: var(--text-color);
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
        </style>
        <script>
            window.onload = () => {{
                const body = document.body;
                const toggle = document.getElementById('theme-toggle');
                const currentTheme = localStorage.getItem('theme');
                if (currentTheme === 'light') {{
                    body.classList.add('light');
                }}
                toggle.onclick = () => {{
                    body.classList.toggle('light');
                    localStorage.setItem('theme', body.classList.contains('light') ? 'light' : 'dark');
                }};
            }};
        </script>
    </head>
    <body>
        <button id="theme-toggle">🌓 Toggle Theme</button>
        <img src="/static/xo-icon.png" alt="XO Logo" style="height: 48px; margin-bottom: 1em;">
        <!-- Persona metadata injected dynamically -->
        <div style="margin-bottom: 1em;">
            <img src="{persona_avatar}" alt="{persona_name} Avatar" class="persona-avatar">
            <strong>{persona_name}</strong>
            <div style="font-size: 0.85em; color: var(--text-color); opacity: 0.85;">
                {{meta.get('role', '') if 'meta' in locals() else ''}}
            </div>
        </div>
        <!-- Optional persona metadata rendering -->
        <div style="margin-top: 0.5em; font-size: 0.9em; color: var(--text-color);">
            {{meta.get('tagline', '') if 'meta' in locals() else ''}}
        </div>
        <div style="font-size: 0.85em; color: var(--text-color); opacity: 0.8;">
            {{meta.get('origin', '') if 'meta' in locals() else ''}}
        </div>
        <div style="font-size: 0.85em; color: var(--text-color); opacity: 0.8;">
            {{meta.get('affiliation', '') if 'meta' in locals() else ''}}
        </div>
        <div style="font-size: 0.85em; color: var(--text-color); opacity: 0.8;">
            {{meta.get('specialty', '') if 'meta' in locals() else ''}}
        </div>
        {html_body}
    </body>
    </html>
    """
    # Render persona role and tagline, using safe access
    if 'meta' in locals():
        html_template = html_template.replace(
            "{{meta.get('role', '') if 'meta' in locals() else ''}}",
            str(meta.get('role', ''))
        ).replace(
            "{{meta.get('tagline', '') if 'meta' in locals() else ''}}",
            str(meta.get('tagline', ''))
        ).replace(
            "{{meta.get('origin', '') if 'meta' in locals() else ''}}",
            str(meta.get('origin', ''))
        ).replace(
            "{{meta.get('affiliation', '') if 'meta' in locals() else ''}}",
            str(meta.get('affiliation', ''))
        ).replace(
            "{{meta.get('specialty', '') if 'meta' in locals() else ''}}",
            str(meta.get('specialty', ''))
        )
    else:
        html_template = html_template.replace(
            "{{meta.get('role', '') if 'meta' in locals() else ''}}", ""
        ).replace(
            "{{meta.get('tagline', '') if 'meta' in locals() else ''}}", ""
        ).replace(
            "{{meta.get('origin', '') if 'meta' in locals() else ''}}", ""
        ).replace(
            "{{meta.get('affiliation', '') if 'meta' in locals() else ''}}", ""
        ).replace(
            "{{meta.get('specialty', '') if 'meta' in locals() else ''}}", ""
        )
    return HTMLResponse(content=html_template, status_code=200)
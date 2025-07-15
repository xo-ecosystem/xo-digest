"""Pulse preview and export tasks with HTML rendering and live reload support."""

from invoke import task
from pathlib import Path
import rich
import markdown
import tempfile
import webbrowser
import time
import re
import os


# HTML Template with Tailwind CDN and dark mode support
HTML_TEMPLATE_PREFIX = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pulse Preview – {slug}</title>
    <meta property="og:title" content="Pulse – {slug}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="https://xo-pulse.netlify.app/{slug}.html" />
    <meta property="og:description" content="XO Pulse: {slug}" />
    <script>
      window.tailwind = {{
        config: {{
          darkMode: 'class',
          theme: {{
            extend: {{
              colors: {{
                xo: '#ff5f7e',
              }},
            }},
          }},
          plugins: [tailwindcssTypography],
        }}
      }};
    </script>
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet" />
    <style>
      html {{ font-family: 'Space Grotesk', sans-serif; }}
      .prose h1, .prose h2 {{ color: #ff5f7e; }}
      .prose blockquote {{
        border-left: 4px solid #ff5f7e;
        padding-left: 1rem;
        font-style: italic;
        color: #4b5563;
      }}
      .dark .prose blockquote {{
        color: #d1d5db;
      }}
      .prose a {{
        color: #ff5f7e;
        text-decoration: underline;
      }}
      .prose a:hover {{
        color: #ec4899;
      }}
      .xo-box {{
        border: 1px solid #ff5f7e;
        background-color: #fef2f2;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      }}
      .dark .xo-box {{
        background-color: #1a1a1a;
      }}
      .pulse-note {{
          background-color: #eff6ff;
          border-left: 4px solid #60a5fa;
          color: #1e40af;
          padding: 1rem;
          margin-bottom: 1rem;
        }}

      .pulse-warning {{
          background-color: #fef9c3;
          border-left: 4px solid #facc15;
          color: #92400e;
          padding: 1rem;
          margin-bottom: 1rem;
        }}

      .pulse-tip {{
          background-color: #dcfce7;
          border-left: 4px solid #4ade80;
          color: #166534;
          padding: 1rem;
          margin-bottom: 1rem;
        }}
    </style>
    <script>
      function toggleDark() {{
        const htmlEl = document.querySelector("html");
        htmlEl.classList.toggle("dark");
      }}
    </script>
</head>
<body class="bg-white text-black dark:bg-black dark:text-white">
    <div class="prose lg:prose-xl mx-auto my-10 px-4">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold">Pulse Preview – {slug}</h1>
            <button onclick="toggleDark()" class="px-4 py-2 rounded bg-gray-800 text-white dark:bg-white dark:text-black">
                Toggle Dark Mode
            </button>
        </div>
"""

HTML_TEMPLATE_SUFFIX = """
    </div>
</body>
</html>"""

# Export HTML Template (simplified for static export)
EXPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pulse – {slug}</title>
    <meta property="og:title" content="Pulse – {slug}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="https://xo-pulse.netlify.app/{slug}.html" />
    <meta property="og:description" content="XO Pulse: {slug}" />
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet" />
    <style>
      html {{ font-family: 'Space Grotesk', sans-serif; }}
      .prose h1, .prose h2 {{ color: #ff5f7e; }}
      .prose blockquote {{
        border-left: 4px solid #ff5f7e;
        padding-left: 1rem;
        font-style: italic;
        color: #4b5563;
      }}
      .prose a {{
        color: #ff5f7e;
        text-decoration: underline;
      }}
      .prose a:hover {{
        color: #ec4899;
      }}
      .pulse-note {{
          background-color: #eff6ff;
          border-left: 4px solid #60a5fa;
          color: #1e40af;
          padding: 1rem;
          margin-bottom: 1rem;
      }}
      .pulse-warning {{
          background-color: #fef9c3;
          border-left: 4px solid #facc15;
          color: #92400e;
          padding: 1rem;
          margin-bottom: 1rem;
      }}
      .pulse-tip {{
          background-color: #dcfce7;
          border-left: 4px solid #4ade80;
          color: #166534;
          padding: 1rem;
          margin-bottom: 1rem;
      }}
    </style>
</head>
<body class="prose lg:prose-xl mx-auto my-10 px-4">
    {content}
</body>
</html>"""

# Default MDX stub template
DEFAULT_MDX_STUB = """# {slug}

Welcome to your new pulse!

:::note Hello World :::

This is a test pulse created automatically. You can edit this file to add your content.

## Features

- **Shortcodes**: Use `:::tip`, `:::note`, `:::warning` for callouts
- **Markdown**: Full markdown support
- **Live Preview**: Use `fab pulse.preview --slug {slug} --html` for live reload

## Getting Started

1. Edit this file: `content/pulses/{slug}/index.mdx`
2. Preview with: `fab pulse.preview --slug {slug} --html`
3. Export with: `fab pulse.export-html --slug {slug}`

Happy writing! ✍️
"""


def parse_shortcodes(md_text):
    """Parse MDX shortcodes and convert to HTML."""
    replacements = {
        r":::\s*tip\s*(.*?):::": r'<div class="pulse-tip">\1</div>',
        r":::\s*warning\s*(.*?):::": r'<div class="pulse-warning">\1</div>',
        r":::\s*note\s*(.*?):::": r'<div class="pulse-note">\1</div>',
    }
    for pattern, replacement in replacements.items():
        md_text = re.sub(pattern, replacement, md_text, flags=re.DOTALL)
    return md_text


def ensure_pulse_exists(slug):
    """Ensure pulse directory and MDX file exist, create stub if missing."""
    pulse_dir = Path("content/pulses") / slug
    index_path = pulse_dir / "index.mdx"
    
    if not pulse_dir.exists():
        pulse_dir.mkdir(parents=True, exist_ok=True)
        rich.print(f"[yellow]📁 Created pulse directory:[/yellow] {pulse_dir}")
    
    if not index_path.exists():
        stub_content = DEFAULT_MDX_STUB.format(slug=slug)
        index_path.write_text(stub_content, encoding="utf-8")
        rich.print(f"[yellow]📝 Created stub MDX file:[/yellow] {index_path}")
        rich.print(f"[blue]💡 Edit the file to add your content![/blue]")
    
    return index_path


def get_pulse_content(slug):
    """Get pulse content, ensuring file exists."""
    index_path = ensure_pulse_exists(slug)
    
    if not index_path.exists():
        rich.print(f"[red]❌ Pulse not found:[/red] {index_path}")
        return None
    
    return index_path.read_text(encoding="utf-8")


@task(help={
    "slug": "Slug of the pulse to preview",
    "html": "Render as HTML with live reload (default: false)"
})
def preview_pulse(c, slug, html=False):
    """
    👀 Preview a pulse as raw Markdown or HTML render with live reload.
    
    Examples:
        fab pulse.preview --slug prose_test
        fab pulse.preview --slug prose_test --html
    """
    content = get_pulse_content(slug)
    if content is None:
        return

    if html:
        try:
            from livereload import Server
            has_livereload = True
        except ImportError:
            has_livereload = False
            rich.print("[yellow]⚠️  livereload not installed. Install with: pip install livereload[/yellow]")

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as tmp:
            html_content = HTML_TEMPLATE_PREFIX.format(slug=slug) + markdown.markdown(parse_shortcodes(content)) + HTML_TEMPLATE_SUFFIX
            tmp.write(html_content)
            tmp_path = tmp.name

        if has_livereload:
            def rebuild():
                try:
                    new_content = get_pulse_content(slug)
                    if new_content:
                        html_content = HTML_TEMPLATE_PREFIX.format(slug=slug) + markdown.markdown(parse_shortcodes(new_content)) + HTML_TEMPLATE_SUFFIX
                        with open(tmp_path, "w", encoding="utf-8") as tmpf:
                            tmpf.write(html_content)
                        rich.print(f"[green]🔄 Rebuilt:[/green] {slug}")
                except Exception as e:
                    rich.print(f"[red]❌ Rebuild failed:[/red] {e}")

            server = Server()
            server.watch(f"content/pulses/{slug}/", rebuild)
            server.watch("tailwind.config.js", rebuild)
            rebuild()  # initial render
            
            rich.print(f"[blue]👀 Watching:[/blue] content/pulses/{slug}/ and tailwind.config.js")
            rich.print(f"[green]🔄 Live server started on http://localhost:5500[/green]")
            rich.print(f"[cyan]🌐 Opening browser...[/cyan]")
            webbrowser.open(f"file://{tmp_path}")
            
            try:
                server.serve(root=Path(tmp_path).parent.as_posix(), port=5500)
            except KeyboardInterrupt:
                rich.print(f"[yellow]🛑 Live reload stopped[/yellow]")
                os.unlink(tmp_path)
        else:
            rich.print(f"[green]🌐 Opening HTML preview in browser:[/green] {tmp_path}")
            webbrowser.open(f"file://{tmp_path}")
    else:
        rich.print(f"[bold cyan]📄 Pulse Preview: {slug}[/bold cyan]")
        rich.print("-" * 60)
        print(content[:1000])
        if len(content) > 1000:
            print("\n... [truncated]")


@task(help={
    "slug": "Slug of the pulse to export"
})
def export_html(c, slug):
    """
    💾 Export pulse as standalone HTML into public/pulses/<slug>.html
    
    Examples:
        fab pulse.export-html --slug prose_test
    """
    content = get_pulse_content(slug)
    if content is None:
        return

    # Convert markdown to HTML with shortcode support
    html_content = markdown.markdown(parse_shortcodes(content))
    
    # Create full HTML document
    html_output = EXPORT_HTML_TEMPLATE.format(
        slug=slug,
        content=html_content
    )

    # Ensure output directory exists
    output_dir = Path("public/pulses")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write HTML file
    output_path = output_dir / f"{slug}.html"
    output_path.write_text(html_output, encoding="utf-8")

    rich.print(f"[green]✅ Exported HTML to:[/green] {output_path}")
    rich.print(f"[blue]📊 File size:[/blue] {output_path.stat().st_size:,} bytes")


@task(help={
    "slug": "Slug of the pulse to edit"
})
def edit_pulse(c, slug):
    """
    ✍️ Open the pulse .mdx in VSCode.
    
    Examples:
        fab pulse.edit --slug prose_test
    """
    index_path = ensure_pulse_exists(slug)
    if not index_path.exists():
        return
    
    rich.print(f"[blue]📝 Opening in VSCode:[/blue] {index_path}")
    c.run(f"code '{index_path}'", pty=True)


# Task collection registration (after all tasks are defined)
from invoke import Collection
ns = Collection("preview")
ns.add_task(preview_pulse, name="preview")
ns.add_task(export_html, name="export-html")
ns.add_task(edit_pulse, name="edit")
from invoke import task, Collection
from textwrap import dedent


@task
def export_html_pulse(c, slug, output=None):
    """
    Export a static HTML preview of a Pulse from .mdx to public/{slug}.html
    """
    from pathlib import Path
    from xo_core.fab_tasks.pulse.preview_utils import generate_html_from_markdown_with_shortcodes as generate_html_from_markdown
    from xo_core.utils.markdown_shortcodes import shortcode_markdown_extension


    md_path = Path(f"content/pulses/{slug}/index.mdx")
    if not md_path.exists():
        # fallback to flat .mdx
        md_path = Path(f"content/pulses/{slug}.mdx")
    if not md_path.exists():
        print(f"❌ Pulse not found: {md_path}")
        return

    output_path = Path(output or f"public/{slug}.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    generate_html_from_markdown(md_path, output_path, extensions=[shortcode_markdown_extension()])
    print("🧠 Applied MDX shortcodes with custom extension.")
    # Ensure Tailwind CDN is embedded if missing
    html = output_path.read_text(encoding="utf-8")
    import re
    # Replace :::note blocks
    html = re.sub(r":::note\n(.*?)\n:::", r'<div class="pulse-note">\1</div>', html, flags=re.DOTALL)
    # Replace :::tip blocks
    html = re.sub(r":::tip\n(.*?)\n:::", r'<div class="pulse-tip">\1</div>', html, flags=re.DOTALL)
    # Replace :::warning blocks
    html = re.sub(r":::warning\n(.*?)\n:::", r'<div class="pulse-warning">\1</div>', html, flags=re.DOTALL)
    if "https://cdn.tailwindcss.com" not in html:
        head_close = html.find("</head>")
        if head_close != -1:
            html = html[:head_close] + '<script src="https://cdn.tailwindcss.com"></script>\n' + html[head_close:]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html, encoding="utf-8")
            print("💡 Embedded Tailwind CDN link.")
    style_block = dedent("""\
    <style>
      .pulse-note {
        @apply bg-blue-50 border-l-4 border-blue-400 text-blue-800 p-4 rounded;
      }
      .pulse-tip {
        @apply bg-green-50 border-l-4 border-green-400 text-green-800 p-4 rounded;
      }
      .pulse-warning {
        @apply bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 p-4 rounded;
      }
    </style>
    """)
    if "</head>" in html:
        html = html.replace("</head>", style_block + "\n</head>")
        output_path.write_text(html, encoding="utf-8")
    print(f"✅ Exported static HTML to: {output_path}")



@task
def watch_mdx_reload(c, slug):
    """
    Watch .mdx file and auto-export HTML on changes.
    """
    import time
    import webbrowser
    from pathlib import Path
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ReloadHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith(".mdx"):
                print("🔁 Change detected, re-exporting HTML...")
                export_html_pulse(c, slug)

    path = f"content/pulses/{slug}/index.mdx"
    if not Path(path).exists():
        path = f"content/pulses/{slug}.mdx"

    if not Path(path).exists():
        print(f"❌ Pulse not found: {path}")
        return

    print(f"👁️ Watching {path} for changes...")
    export_html_pulse(c, slug)
    webbrowser.open(str(Path("public") / f"{slug}.html"))

    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(Path(path).parent), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


ns = Collection("pulse")
ns.add_task(export_html_pulse, name="export-html")
ns.add_task(watch_mdx_reload, name="watch")

# Ensure prose_test exists before wiring preview
if __name__ == "__main__":
    from pathlib import Path
    test_slug = "prose_test"
    md_test_path = Path(f"content/pulses/{test_slug}/index.mdx")
    if not md_test_path.exists():
        md_test_path.parent.mkdir(parents=True, exist_ok=True)
        md_test_path.write_text("# Prose Test\n\n:::note\nWelcome to the prose test.\n:::\n", encoding="utf-8")
        print(f"📝 Created placeholder test pulse: {md_test_path}")
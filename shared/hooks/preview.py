import os
from pathlib import Path


def hook_preview(persona, content=None):
    """Preview plugin hook for generating Markdown previews"""
    preview_dir = Path("public/previews")
    preview_dir.mkdir(exist_ok=True)

    preview_content = f"""# {persona.title()} Preview

## Generated Content
{content or f"Preview for {persona} persona"}

## Metadata
- Persona: {persona}
- Generated: {os.popen('date').read().strip()}
"""

    preview_file = preview_dir / f"{persona}_preview.md"
    with open(preview_file, "w") as f:
        f.write(preview_content)

    print(f"🪞 Preview generated → {preview_file}")

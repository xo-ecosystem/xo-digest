# vault_log.py
# Minimal placeholder for digest logic

import os

def generate_digest():
    """Render Vault logbook digest preview and write to .mdx for Brie or CI use."""
    output_dir = "vault/daily"
    os.makedirs(output_dir, exist_ok=True)
    preview_path = os.path.join(output_dir, "preview.md")

    mdx_content = "# Placeholder digest\n\n> Logbook rendering is currently disabled."
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(mdx_content)

    print(f"✅ Digest preview written to {preview_path}")
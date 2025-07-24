from invoke import task
from pathlib import Path
import shutil
from PIL import Image

@task(help={"persona": "Persona name (e.g., seal_flame)", "bg": "Optional hoodie background image"})
def preview_merch(c, persona="seal_flame", bg="hoodie_black.png"):
    """
    🧥 Generate print preview mockups by merging persona scrolls with a hoodie background.
    """
    root = Path("~/xo-core").expanduser()
    persona_dir = root / f"xo_persona_{persona}"
    preview_dir = persona_dir / "merch_mockups"
    preview_dir.mkdir(exist_ok=True)

    background_path = persona_dir / bg
    if not background_path.exists():
        print(f"⚠️ Background image not found: {background_path}")
        return

    scrolls = sorted(persona_dir.glob("transparent_scroll_*.webp"))
    if not scrolls:
        print(f"⚠️ No transparent scrolls found in {persona_dir}")
        return

    for scroll in scrolls:
        hoodie = Image.open(background_path).convert("RGBA")
        overlay = Image.open(scroll).convert("RGBA")
        hoodie = hoodie.resize(overlay.size)
        mockup = Image.alpha_composite(hoodie, overlay)
        out_path = preview_dir / f"mockup_{scroll.name.replace('.webp', '.png')}"
        mockup.save(out_path)
        print(f"✅ Created mockup: {out_path.name}")


# --- New tasks ---

@task(help={"persona": "Persona name", "drop": "Drop to link into", "copy": "Copy files instead of symlinking"})
def assets_link(c, persona="seal_flame", drop="message_bottle", copy=False):
    """🔗 Link or copy persona assets into drop.assets/<drop> folder."""
    root = Path("~/xo-core").expanduser()
    persona_dir = root / f"xo_persona_{persona}"
    drop_dir = root / f"src/xo_core/vault/seals/eighth/drop.assets/{drop}"
    drop_dir.mkdir(parents=True, exist_ok=True)
    asset_files = sorted(persona_dir.glob("transparent_scroll_*.webp")) + [
        persona_dir / "avatar_print_transparent.png"
    ]
    for asset in asset_files:
        dest = drop_dir / asset.name
        if copy:
            shutil.copy(asset, dest)
            print(f"📄 Copied {asset.name} to {drop}")
        else:
            if not dest.exists():
                dest.symlink_to(asset)
                print(f"🔗 Linked {asset.name} to {drop}")


@task(help={"persona": "Persona name"})
def assets_cleanup(c, persona="seal_flame"):
    """🧼 Clean up mockups and broken symlinks in persona folder."""
    root = Path("~/xo-core").expanduser()
    persona_dir = root / f"xo_persona_{persona}"
    mockups_dir = persona_dir / "merch_mockups"
    if mockups_dir.exists():
        for f in mockups_dir.glob("*.png"):
            f.unlink()
            print(f"🗑️ Removed {f.name}")
    for file in persona_dir.iterdir():
        if file.is_symlink() and not file.exists():
            file.unlink()
            print(f"🧹 Cleaned broken symlink: {file.name}")


@task(help={"persona": "Persona name"})
def mockup_bundle(c, persona="seal_flame"):
    """📦 Zip all mockups into a bundle for download or upload."""
    from zipfile import ZipFile
    root = Path("~/xo-core").expanduser()
    mockup_dir = root / f"xo_persona_{persona}/merch_mockups"
    zip_path = mockup_dir / "mockups_bundle.zip"
    if not mockup_dir.exists():
        print("❌ No mockup directory found.")
        return
    with ZipFile(zip_path, "w") as zipf:
        for f in mockup_dir.glob("*.png"):
            zipf.write(f, arcname=f.name)
            print(f"📦 Added {f.name} to bundle.")
    print(f"✅ Bundle ready: {zip_path}")
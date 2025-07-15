import os
from pathlib import Path
from invoke import task

CONTENT_DIR = Path("content/pulses")

@task(help={"slug": "Slug name of the pulse to delete"})
def delete_pulse(c, slug):
    """
    Delete a pulse and its associated files (.mdx, .coin.yml, .comments.mdx).
    """
    pulse_path = CONTENT_DIR / slug

    deleted_files = []
    if not pulse_path.exists():
        print(f"⚠️ Pulse folder not found: {pulse_path}")
        return

    for ext in [".mdx", ".comments.mdx", ".coin.yml"]:
        f = pulse_path / f"{slug}{ext}"
        if f.exists():
            f.unlink()
            deleted_files.append(str(f))

    # Optionally remove the folder if empty
    if pulse_path.exists() and not any(pulse_path.iterdir()):
        pulse_path.rmdir()
        print(f"🗑️ Removed empty folder: {pulse_path}")

    if deleted_files:
        print("✅ Deleted:")
        for f in deleted_files:
            print(f"  - {f}")
    else:
        print("ℹ️ No deletable files found.")


from invoke import Collection

ns = Collection()
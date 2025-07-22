"""Pulse-related Fabric tasks for xo-core-clean."""

from invoke import task
import sys
sys.path.append(".")
from scripts.ipfs_upload import upload_to_ipfs
from invoke import Collection


@task
def preview(c, drop="eighth_seal_3d"):
    """
    🔍 Render vault preview content from drop.assets into public preview folder.
    """
    from pathlib import Path
    import shutil

    src = Path(f"src/xo_core/vault/seals/eighth/drop.assets/{drop}/metadata")
    dst = Path(f"public/vault/previews/{drop}")
    dst.mkdir(parents=True, exist_ok=True)

    for file in src.glob("*.webp"):
        shutil.copy(file, dst / file.name)
    for file in src.glob("*.yml"):
        shutil.copy(file, dst / file.name)

    print(f"✅ Preview synced to: {dst}")


@task
def new(c, slug):
    """📦 Create a new pulse entry."""
    print(f"🆕 Pulse created for: {slug}")


@task
def sync(c):
    """🔄 Sync pulses."""
    print("🔁 Pulses synced")


@task
def archive_all(c):
    """🗃️ Archive all pulses."""
    print("📦 All pulses archived")


@task
def upload(c, file_path):
    """🌀 Upload a file to IPFS and return the hash + URL."""
    result = upload_to_ipfs(file_path)
    print(f"📡 Uploaded to IPFS:\nHash: {result['Hash']}\nURL: {result['URL']}")


@task
def sign(c, slug):
    """✍️ Sign a pulse (stub)."""
    print(f"✅ Pulse signed: {slug}")


@task
def deploy_eighth_seal_preview(c):
    """📦 Deploy the eighth_seal_3d preview to public preview folder and trigger explorer deploy."""
    c.run("xo-fab pulse.preview --drop=eighth_seal_3d")
    c.run("xo-fab explorer.deploy")


ns = Collection("pulse")
ns.add_task(new, name="new")
ns.add_task(sync, name="sync")
ns.add_task(archive_all, name="archive")
ns.add_task(upload, name="upload")
ns.add_task(sign, name="sign")
ns.add_task(preview, name="preview")
ns.add_task(deploy_eighth_seal_preview, "drop.deploy")

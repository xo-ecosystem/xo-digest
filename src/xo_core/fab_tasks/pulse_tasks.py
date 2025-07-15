"""Pulse-related Fabric tasks for xo-core-clean."""

from invoke import task
import sys
sys.path.append(".")
from scripts.ipfs_upload import upload_to_ipfs
from invoke import Collection


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


ns = Collection("pulse")
ns.add_task(new, name="new")
ns.add_task(sync, name="sync")
ns.add_task(archive_all, name="archive")
ns.add_task(upload, name="upload")
ns.add_task(sign, name="sign")

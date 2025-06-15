"""Pulse-related Fabric tasks for xo-core-clean."""

from invoke import task


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

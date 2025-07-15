from invoke import task
from pathlib import Path
import shutil

def _lazy_generate_test_pulse(c, slug):
    """Lazy import and call generate_test_pulse to avoid circular imports."""
    try:
        from ._shared_data import generate_test_pulse as _generate
    except ImportError:
        # Fallback for script execution
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from _shared_data import generate_test_pulse as _generate
    
    result = _generate(c, slug)
    print(f"🧪 Generated test pulse: {result.get('slug', slug)}")
    return result

@task(help={"slug": "Slug name of the pulse to sync"})
def sync(c, slug):
    """
    🔄 Simulate syncing a pulse by copying .mdx content and .signed file to a .synced directory
    """
    if slug == "test_pulse":
        _lazy_generate_test_pulse(c, slug)

    pulse_path = Path(f"content/pulses/{slug}/{slug}.mdx")
    signed_path = Path(f"vault/.signed/{slug}.signed")
    synced_dir = Path("vault/.synced")
    synced_dir.mkdir(parents=True, exist_ok=True)

    if not pulse_path.exists():
        print(f"❌ Pulse not found: {pulse_path}")
        return

    content = pulse_path.read_text()
    synced_path = synced_dir / f"{slug}.mdx"
    synced_path.write_text(content)
    print(f"🔄 Pulse synced: {slug}.mdx")

    if signed_path.exists():
        shutil.copy(signed_path, synced_dir / signed_path.name)
        print(f"✅ Signed file copied: {signed_path.name}")
    else:
        print(f"⚠️ Signed file not found: {signed_path.name}")

@task
def sync_all(c):
    """
    🔁 Sync all .mdx pulses in content/pulses/ that have not yet been synced
    """
    print("📦 Syncing all pulses...")
    pulse_dirs = Path("content/pulses").glob("*/")
    for dir_path in pulse_dirs:
        slug = dir_path.name
        sync(c, slug=slug)

@task
def dev(c):
    """
    🧪 Run full test/dev flow for test_pulse (new, sign, sync, archive)
    """
    print("⚙️ Running pulse.dev sequence...")
    _lazy_generate_test_pulse(c, "test_pulse")
    c.run("xo-fab pulse.new --slug test_pulse")
    c.run("xo-fab pulse.sign --slug test_pulse")
    c.run("xo-fab pulse.sync --slug test_pulse")
    c.run("xo-fab pulse.archive --slug test_pulse --dry-run")
    c.run("xo-fab pulse.sync_all")

from invoke import Collection

ns = Collection("pulse")
ns.add_task(sync, name="sync")
ns.add_task(sync_all, name="sync_all")
ns.add_task(dev, name="dev")

__all__ = ["ns"]
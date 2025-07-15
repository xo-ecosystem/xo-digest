

from invoke import task, Collection
from pathlib import Path


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


@task
def dev(ctx):
    """Run full pulse dry-run development flow."""
    slug = "test_pulse"
    print("⚙️ Running pulse.dev sequence...")

    _lazy_generate_test_pulse(ctx, slug=slug)
    
    # Import other functions lazily to avoid circular imports
    try:
        from .new import new_pulse
        from .sign import sign
        from .archive import archive
        from .sync import sync
        from .publish import publish
        
        new_pulse(ctx, slug=slug)
        sign(ctx, slug=slug, dry_run=True)
        archive(ctx, slug=slug, dry_run=True)
        sync(ctx, slug=slug, dry_run=True)
        publish(ctx, slug=slug, dry_run=True)
    except ImportError as e:
        print(f"⚠️ Some modules not available: {e}")


# Create namespace
ns = Collection("dev")
ns.add_task(dev)
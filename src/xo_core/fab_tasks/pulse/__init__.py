"""Pulse task collection for XO Core."""

from invoke import Collection, task

# Core pulse task imports
from .archive import archive
from .delete import delete_pulse
from .new import new_pulse as new
from .sign import sign
from .sync import dev, sync

# Auto workflow task
try:
    from .auto import ns as auto_ns
except ImportError as e:
    auto_ns = None
    print(f"[pulse] Auto workflow module not loaded: {e}")

@task(help={"slug": "Slug name for the test pulse (default: test_pulse)"})
def _lazy_generate_test_pulse(c, slug="test_pulse"):
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

try:
    from .publish import publish
except ImportError as e:
    publish = None
    print(f"[pulse] Optional publish module not loaded: {e}")

# Optional preview/export tasks
try:
    from .preview import edit_pulse, export_html, preview_pulse
except ImportError as e:
    preview_pulse = export_html = edit_pulse = None
    print(f"[pulse] Optional preview module not loaded: {e}")

# Create the pulse namespace
ns = Collection("pulse")

# Core pulse operations
ns.add_task(sync, name="sync")
ns.add_task(sign, name="sign")
ns.add_task(new, name="new")
ns.add_task(archive, name="archive")
ns.add_task(delete_pulse, name="delete")
ns.add_task(_lazy_generate_test_pulse, name="generate-test-pulse")
ns.add_task(dev, name="dev")
if auto_ns:
    ns.add_collection(auto_ns, name="auto")
if publish:
    ns.add_task(publish, name="publish")

# Auto task is already registered as a collection above

# Preview and export tasks
if preview_pulse:
    ns.add_task(preview_pulse, name="preview")
if export_html:
    ns.add_task(export_html, name="export-html")
if edit_pulse:
    ns.add_task(edit_pulse, name="edit")

__all__ = ["ns"]


def get_ns():
    return ns
# This module already exposes get_ns() and is registered in fabfile.py
# No changes needed here
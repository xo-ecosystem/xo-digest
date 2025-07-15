"""Pulse task collection for XO Core."""

from invoke import Collection

# Core pulse task imports
from .archive import archive
from .delete import delete_pulse
from .test import generate_test_pulse
from .sync import sync, dev
from .new import new_pulse as new
from .sign import sign
try:
    from .publish import publish_pulse as publish
except ImportError as e:
    publish = None
    print(f"[pulse] Optional publish module not loaded: {e}")

# Optional preview/export tasks
try:
    from .preview import preview_pulse, export_html, edit_pulse
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
ns.add_task(generate_test_pulse, name="generate-test-pulse")
ns.add_task(dev, name="dev")
if publish:
    ns.add_task(publish, name="publish")

# Preview and export tasks
if preview_pulse:
    ns.add_task(preview_pulse, name="preview")
if export_html:
    ns.add_task(export_html, name="export-html")
if edit_pulse:
    ns.add_task(edit_pulse, name="edit")

__all__ = ["ns"]
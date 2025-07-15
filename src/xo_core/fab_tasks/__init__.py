"""Root Fabric tasks collection and validation setup."""

from invoke import Collection

# Aggregate all task namespaces under the root `tasks` collection
tasks = Collection("tasks")


# Import and add summary tasks to the main collection
def add_summary_tasks():
    from .summary_tasks import ns as summary_ns

    tasks.add_collection(summary_ns)


try:
    from .pulse.preview import export_html
    from .pulse.publish import publish
except ImportError:
    export_html = None
    publish = None
# Import sub-namespaces and default tasks
from .pulse_namespace import ns as pulse_ns
from .validate_tasks import validate_tasks as _validate_tasks_task

if export_html:
    pulse_ns.add_task(export_html, name="export-html")
if publish:
    pulse_ns.add_task(publish, name="publish")

# A collection that exposes the single "validate-tasks" Invoke task.
# The tests expect to access it via:  validate_tasks["validate-tasks"]
validate_tasks = Collection("validate_tasks")
validate_tasks.add_task(_validate_tasks_task, name="validate-tasks", default=True)

tasks.add_collection(pulse_ns)
tasks.add_collection(validate_tasks)
add_summary_tasks()

try:
    from .vault import ns as vault_ns
    tasks.add_collection(vault_ns, name="vault")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Vault namespace not loaded: {e}")

from .help_card import ns as help_card_ns
from .bundle import ns as bundle_ns
from .test_all import ns as test_all_ns
from .full_publish import ns as full_ns

# Optional inbox import (safer with dynamic fallback)
import logging
try:
    from .inbox import ns as inbox_ns
except Exception as e:
    logging.warning(f"⚠️ Failed to import inbox tasks: {type(e).__name__}: {e}")
else:
    try:
        tasks.add_collection(inbox_ns, name="inbox")
    except Exception as inner_e:
        logging.warning(f"⚠️ Failed to register inbox namespace: {type(inner_e).__name__}: {inner_e}")

__all__ = ["help_card_ns", "bundle_ns", "test_all_ns"]

# This module exposes the full task tree for use in `fabfile.py`
# xo_core/fab_tasks/__init__.py

from .drop_tasks import bundle
from invoke import Collection

drop_ns = Collection("drop")
drop_ns.add_task(bundle)
tasks.add_collection(drop_ns)

from .pulse_tasks import ns as pulse_tasks_ns
from .pulse_namespace import ns as pulse_ns
from .vault_tasks import ns as vault_tasks_ns

# Register all main collections
try:
    tasks.add_collection(drop_ns, name="drop")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Drop namespace not loaded: {e}")
try:
    tasks.add_collection(pulse_tasks_ns, name="pulse_tasks")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Pulse tasks namespace not loaded: {e}")
try:
    tasks.add_collection(pulse_ns, name="pulse")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Pulse namespace not loaded: {e}")
try:
    tasks.add_collection(vault_tasks_ns, name="vault_tasks")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Vault tasks namespace not loaded: {e}")

# Doctor report task
from invoke import task

_loaded = []
_skipped = []
_failed = []

def _collect_status():
    global _loaded, _skipped, _failed
    _loaded = [k for k in tasks.collections.keys()]
    # For demo, skipped/failed are empty unless you want to track more
    # You could enhance this by tracking in the try/excepts above

@task
def doctor_report(c):
    """Prints a report of loaded, skipped, and failed task modules."""
    _collect_status()
    print("\n✔️ Loaded task namespaces:")
    for ns in _loaded:
        print(f"  - {ns}")
    if _skipped:
        print("\n⚠️ Skipped modules:")
        for ns in _skipped:
            print(f"  - {ns}")
    if _failed:
        print("\n❌ Failed imports:")
        for ns, err in _failed:
            print(f"  - {ns}: {err}")
    print("\n🩺 Doctor report complete.\n")

tasks.add_task(doctor_report, name="doctor.report")
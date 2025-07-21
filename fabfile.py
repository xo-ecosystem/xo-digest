from xo_core.fab_tasks.dev_doctor_tasks import ns as dev_doctor_ns
from xo_core.fab_tasks.pulse_tasks import ns as pulse_ns
from invoke import task, Collection
from pathlib import Path
from xo_core.fab_tasks.ipfs_tasks import ns as ipfs_ns
from xo_core.fab_tasks import pulse_tasks

# Add tasks to pulse namespace if they exist
try:
    pulse_ns.add_task(pulse_tasks.sign, "sign")
except AttributeError:
    pass  # Task already registered in the collection

try:
    pulse_ns.add_task(pulse_tasks.archive_all, "archive")
except AttributeError:
    pass  # Task already registered in the collection

try:
    pulse_ns.add_task(pulse_tasks.sync, "sync")
except AttributeError:
    pass  # Task already registered in the collection

@task
def push_logbook(c):
    """Simple logbook push task for testing."""
    print("📔 Push logbook task - simplified for testing")
    print("Use xo-fab ipfs.test-connection to test IPFS setup")

@task(help={"verbose": "Enable verbose output", "fix": "Attempt auto-fixes for failed rules"})
def doctor(c, verbose=False, fix=False):
    """Root-level doctor task that forwards to dev.doctor."""
    from xo_core.fab_tasks.dev_doctor_tasks import doctor as dev_doctor
    return dev_doctor(c, verbose=verbose, fix=fix)

# Create main namespace
ns = Collection()

# Add IPFS tasks
try:
    ns.add_collection(ipfs_ns, name="ipfs")
except Exception as e:
    import logging
    logging.warning(f"⚠️ IPFS namespace not loaded: {e}")

# Add dev_doctor tasks
try:
    ns.add_collection(dev_doctor_ns, name="dev")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Dev doctor namespace not loaded: {e}")

# Add pulse tasks
try:
    ns.add_collection(pulse_ns, name="pulse")
except Exception as e:
    import logging
    logging.warning(f"⚠️ Pulse namespace not loaded: {e}")

# Add drop_patch tasks
try:
    from xo_core.fab_tasks.drop_patch import ns as drop_patch_ns
    ns.add_collection(drop_patch_ns, name="drop")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Drop patch namespace not loaded: {e}")

# Add drop_meta_sync tasks
try:
    from xo_core.fab_tasks.drop_meta_sync import ns as drop_meta_sync_ns
    ns.add_collection(drop_meta_sync_ns, name="meta")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Drop meta sync namespace not loaded: {e}")

# Add sign_pulse tasks, if available
try:
    from xo_core.fab_tasks.vault.sign_pulse import ns as sign_pulse_ns
    ns.add_collection(sign_pulse_ns, name="sign_pulse")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Sign pulse namespace not loaded: {e}")

# Add sign_pulse_test tasks, if available
try:
    from xo_core.fab_tasks.vault.sign_pulse_test import ns as sign_pulse_test_ns
    ns.add_collection(sign_pulse_test_ns, name="sign_pulse_test")
except ImportError as e:
    import logging
    logging.warning(f"⚠️ Sign pulse test namespace not loaded: {e}")

# Add root-level doctor task
ns.add_task(doctor, "doctor")

# Define the default namespace
namespace = ns
import os
import logging

from invoke import task

logger = logging.getLogger(__name__)

@task
def bootstrap(c):
    """
    ♻️ Rebuild folder links and scaffold initial vault layout
    """
    folders = [
        "fab_tasks",
        "scripts",
        "apps",
        "content/pulses",
        "vault",
        "agent0",
        "dashboard",
        "drops",
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📂 Ensured: {folder}")
    os.system("python scripts/regen_stubs.py")
    print("✅ Bootstrap complete.")


# Add required ns variable for fabfile.py integration
from invoke import Collection
ns = Collection(bootstrap)

try:
    from xo_core.fab_tasks.tools import describe, meta_generate, doctor
    ns.add_collection(describe.ns, name="tools-describe")
    ns.add_collection(meta_generate.ns, name="tools-meta-generate")
    ns.add_collection(doctor.ns, name="tools-doctor")
except (ImportError, AttributeError) as e:
    logger.warning(f"⚠️ Skipping tools submodules: {type(e).__name__}: {e}")

try:
    from xo_core.fab_tasks import pulse

    for submod, name in [
        ("delete", "pulse-delete"),
        ("preview", "pulse-preview"),
        ("_shared_data", "pulse-shared-data"),
        ("pin_to_arweave", "pulse-pin-to-arweave"),
        ("review", "pulse-review"),
    ]:
        try:
            mod = getattr(pulse, submod)
            ns.add_collection(mod.ns, name=name)
        except AttributeError as e:
            logger.warning(f"⚠️ Skipping pulse.{submod}: {type(e).__name__}: {e}")
except ImportError as e:
    logger.warning(f"⚠️ Skipping pulse submodules: {type(e).__name__}: {e}")

from invoke import Collection

ns = Collection()

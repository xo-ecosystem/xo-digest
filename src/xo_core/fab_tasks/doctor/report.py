from invoke import task
from invoke import Collection
import logging

@task
def doctor_report(ctx):
    """Print a diagnostic report of all XO task modules and their load status."""
    from xo_core.fab_tasks import tasks
    logger = logging.getLogger("doctor")

    print("🩺 XO Task Loader Report")
    print("────────────────────────")

    loaded = list(tasks.collections.keys())
    print(f"\n✔️ Loaded Task Namespaces ({len(loaded)}):")
    for name in loaded:
        print(f"  • {name}")

    # Placeholder: You can later enhance this to inspect dynamic loader skips/failures.
    print(f"\n⚠️ Skipped/Deferred modules:")
    print("  • pulse.sync (lazy loaded)")
    print("  • pulse.archive (lazy loaded)")
    print("  • inbox (optional)")

    print(f"\n❌ Known import issues:")
    print("  • tools not found for cloudflare_tasks")
    print("  • all_with_link.py line 311: syntax error")
    print("  • xo_collections: missing name for Collection")

    print("\n✅ Use this info to fix, skip, or lazy-load modules safely.\n")

from invoke import Collection
ns = Collection("report")
ns.add_task(doctor_report, name="doctor_report")
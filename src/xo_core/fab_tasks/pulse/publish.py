from invoke import task
from pathlib import Path
import shutil
import os

@task(
    help={
        "slug": "Slug of the pulse to publish",
        "dry_run": "Perform a dry-run without making changes",
        "pin_ipfs": "Pin the pulse to Arweave/IPFS",
        "webhook": "Trigger webhook after publishing"
    }
)
def publish(c, slug=None, dry_run=False, pin_ipfs=False, webhook=False):
    """
    📤 Finalize a signed pulse for public use and optionally pin to IPFS/Arweave.
    Usage: xo-fab pulse.publish --slug <slug> [--dry-run] [--pin-ipfs] [--webhook]
           xo-fab pulse.publish:<slug> [--dry-run] [--pin-ipfs] [--webhook]
    """
    if not slug:
        print("❌ No slug provided. Use --slug <name> or pulse.publish:<slug>")
        return

    content_dir = Path("content/pulses") / slug
    signed_dir = Path("vault/.signed") / slug
    publish_dir = Path("vault/.published") / slug

    if not signed_dir.exists():
        print(f"❌ Signed pulse not found: {signed_dir}")
        return

    mdx_files = list(signed_dir.glob("*.mdx"))
    if not mdx_files:
        print(f"❌ No .mdx file found in signed pulse: {signed_dir}")
        return False

    print(f"📤 Publishing pulse: {slug}")
    if dry_run:
        print(f"🔍 [Dry-run] Would copy from {signed_dir} to {publish_dir}")
        return

    publish_dir.mkdir(parents=True, exist_ok=True)
    for file in signed_dir.glob("*"):
        dest = publish_dir / file.name
        shutil.copy2(file, dest)
        print(f"✅ Copied: {file.name}")

    if not dry_run:
        from invoke import run

        # Auto-call export-html
        print("🧠 Exporting HTML version of pulse...")
        run(f"xo-fab pulse.export-html --slug={slug}")

        # Optionally push latest digest
        if webhook:
            print("📡 Pushing latest digest...")
            run("xo-fab vault.digest.push")

    # Optional: Pin to IPFS/Arweave here
    arweave_keyfile = os.getenv("ARWEAVE_KEYFILE")
    if pin_ipfs:
        # Pin to Arweave
        if not arweave_keyfile or not Path(arweave_keyfile).expanduser().is_file():
            print("⚠️  Skipping Arweave pinning: ARWEAVE_KEYFILE not found.")
        else:
            print("📡 Uploading to Arweave...")
            result = run(f"python scripts/pin_to_arweave.py --slug={slug}", warn=True)
            if result.ok:
                print("✅ Successfully pinned to Arweave.")
            else:
                print("❌ Arweave pinning failed.")

        # Optionally pin to Lighthouse
        lighthouse_token = os.getenv("LIGHTHOUSE_API_TOKEN")
        if lighthouse_token:
            print("📡 Uploading to Lighthouse...")
            result = run(f"python scripts/pin_to_lighthouse.py --slug={slug}", warn=True)
            if result.ok:
                print("✅ Successfully pinned to Lighthouse.")
            else:
                print("❌ Lighthouse pinning failed.")
        else:
            print("⚠️  Skipping Lighthouse pinning: LIGHTHOUSE_API_TOKEN not set.")

        # Optionally pin to Thirdweb IPFS
        print("📦 Uploading to Thirdweb IPFS...")
        result = run(f"python scripts/pin_to_thirdweb.py --slug={slug}", warn=True)
        if result.ok:
            print("✅ Successfully pinned to Thirdweb IPFS.")
        else:
            print("❌ Thirdweb IPFS pinning failed.")

    if webhook:
        print("📣 Triggering publish webhook...")
        result = run(f"python scripts/send_webhook.py --event pulse_publish --status success --slug {slug}", warn=True)
        if result.ok:
            print("✅ Webhook sent.")
        else:
            print("❌ Webhook failed.")

    print(f"✅ Published: {slug}")
    return True

from invoke import Collection

ns = Collection("pulse")
ns.add_task(publish)

# Register namespace for discovery
# If DynamicTaskLoader.discover_namespaces is a static method, call it directly; otherwise, instantiate.
try:
    from xo_core.dynamic_loader import DynamicTaskLoader
    # If discover_namespaces is a staticmethod
    DynamicTaskLoader.discover_namespaces()
except ImportError:
    pass

namespace = ns
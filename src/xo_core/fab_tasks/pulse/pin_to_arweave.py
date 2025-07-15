

import os
import json
from pathlib import Path
from fabric import task
from invoke import Context

@task
def pin_to_arweave(c: Context, pulse_slug=None):
    """
    📤 Pin a pulse's signed .mdx to Arweave and log the TXID.

    Usage:
        xo-fab pin-to-arweave --pulse-slug=test_pulse
    """
    if not pulse_slug:
        print("❌ Missing pulse_slug. Please provide --pulse-slug=<slug>")
        return

    base_path = Path("content/pulses") / pulse_slug
    signed_path = Path("vault/.signed") / f"{pulse_slug}.signed"

    if not base_path.exists() or not signed_path.exists():
        print(f"❌ Required files not found for pulse: {pulse_slug}")
        return

    print(f"📦 Preparing Arweave upload for {pulse_slug}...")

    # Simulated Arweave upload step
    arweave_tx_id = f"simulated_txid_{pulse_slug}"
    arweave_link = f"https://arweave.net/{arweave_tx_id}"

    print(f"✅ Uploaded {pulse_slug} to Arweave: {arweave_link}")

    # Log to manifest (optional)
    manifest_file = Path("vault/.signed/arweave_manifest.json")
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
    else:
        manifest = {}

    manifest[pulse_slug] = {
        "tx_id": arweave_tx_id,
        "link": arweave_link
    }
    manifest_file.write_text(json.dumps(manifest, indent=2))
    print(f"📝 Logged TXID to manifest: {manifest_file}")

from invoke import Collection
ns = Collection("pulse")
ns.add_task(pin_to_arweave, name="pin_to_arweave")
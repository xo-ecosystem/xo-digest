import json
from pathlib import Path

from invoke import Collection, task


@task(help={"slug": "Name of the bundle (slug)"})
def mint(c, slug):
    print(f"🪙 Simulating mint for: {slug}")
    bundle_path = Path(f"./vault/{slug}_bundle/metadata.json")
    if not bundle_path.exists():
        print("❌ metadata.json not found in bundle.")
        return

    metadata = json.loads(bundle_path.read_text())
    print(f"✅ Metadata loaded: {metadata['name']}")

    log_path = Path(f"./vault/{slug}_bundle/.mint.log.json")
    log = {
        "slug": slug,
        "status": "dry_run",
        "name": metadata.get("name"),
        "description": metadata.get("description"),
        "image": metadata.get("image"),
        "attributes": metadata.get("attributes", []),
        "signature": metadata.get("signature", {}),
    }
    log_path.write_text(json.dumps(log, indent=2))
    print(f"📄 Dry-run logged to {log_path}")


ns = Collection("nft")
ns.add_task(mint, name="mint")

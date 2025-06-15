import json
from pathlib import Path

from invoke import Collection, task


@task(help={"slug": "Name of the bundle (slug)"})
def mint(c, slug):
    print(f"🪙 Simulating mint for: {slug}")
    local_path = Path(f"./vault/{slug}_bundle/metadata.json")
    fallback_path = Path(f"/mnt/data/vault/{slug}_bundle/metadata.json")

    bundle_path = local_path if local_path.exists() else fallback_path
    if not bundle_path.exists():
        print("❌ metadata.json not found in either expected location.")
        return

    metadata = json.loads(bundle_path.read_text())
    print(f"✅ Metadata loaded: {metadata['name']}")

    log_path = bundle_path.parent / ".mint.log.json"
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

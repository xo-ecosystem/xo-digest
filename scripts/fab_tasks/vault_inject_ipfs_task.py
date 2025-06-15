import json
from pathlib import Path

from invoke import Collection, task


@task(help={"slug": "Vault slug", "cid": "IPFS content identifier (CID)"})
def inject_ipfs(c, slug, cid):
    path = Path(f"./vault/{slug}_bundle/metadata.json")
    if not path.exists():
        print(f"❌ metadata.json not found for slug: {slug}")
        return

    data = json.loads(path.read_text())
    data["image"] = f"ipfs://{cid}/image.png"
    data["external_url"] = f"https://{cid}.ipfs.nftstorage.link"

    # Save backup
    backup = path.with_suffix(".original.json")
    if not backup.exists():
        backup.write_text(json.dumps(data, indent=2))

    # Write updated metadata
    path.write_text(json.dumps(data, indent=2))
    print(
        f"""✅ metadata.json updated with IPFS links:
  - image: {data['image']}
  - external_url: {data['external_url']}"""
    )


ns = Collection("vault")
ns.add_task(inject_ipfs, name="inject-ipfs")

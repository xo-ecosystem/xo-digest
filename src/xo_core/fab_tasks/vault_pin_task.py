import os
from pathlib import Path

import requests
from invoke import Collection, task

NFT_STORAGE_TOKEN = os.getenv("NFT_STORAGE_TOKEN")


@task(help={"slug": "Name of the vault bundle (slug)"})
def pin(c, slug):
    print(f"📦 Pinning bundle: {slug}")
    base_path = Path(f"./vault/{slug}_bundle")
    if not base_path.exists():
        print("❌ Bundle directory not found.")
        return

    files = list(base_path.glob("*"))
    if not files:
        print("⚠️ No files found in bundle.")
        return

    headers = {
        "Authorization": f"Bearer {NFT_STORAGE_TOKEN}",
    }

    # Construct multipart form-data manually
    multiple_files = [("file", (f.name, f.open("rb"))) for f in files]

    print("⏳ Uploading to nft.storage...")
    res = requests.post(
        "https://api.nft.storage/upload", headers=headers, files=multiple_files
    )
    if res.status_code == 200:
        cid = res.json()["value"]["cid"]
        print(f"✅ Uploaded to IPFS: ipfs://{cid}")
        print(f"🔗 Gateway: https://{cid}.ipfs.nftstorage.link/")
    else:
        print(f"❌ Upload failed: {res.status_code}")
        print(res.text)


ns = Collection("vault")
ns.add_task(pin, name="pin")

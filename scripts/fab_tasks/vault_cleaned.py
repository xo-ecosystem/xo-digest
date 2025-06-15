# fab_tasks/vault.py
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from arweave import Transaction, Wallet
from invoke import Collection, task

NFT_STORAGE_TOKEN = os.environ.get("NFT_STORAGE_TOKEN")
ARWEAVE_KEY_PATH = "secrets/arweave.json"


def upload_logbook_to_arweave():
    print("🌐 Skipping Arweave logbook upload for now.")


def upload_to_ipfs_via_http(filepath: Path):
    token = os.getenv("NFT_STORAGE_TOKEN")
    if not token:
        print("❌ NFT_STORAGE_TOKEN not set")
        return None
    with filepath.open("rb") as f:
        res = requests.post(
            "https://api.nft.storage/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (filepath.name, f)},
        )
    if res.status_code == 200:
        cid = res.json()["value"]["cid"]
        print(f"📦 IPFS CID for {filepath.name}: {cid}")
        return cid
    print(f"❌ IPFS upload failed: {res.status_code} {res.text}")
    return None


@task
def init(ctx):
    print("🔐 XO Vault initialized")


@task(help={"path": "Path to .mdx pulse"})
def sign_pulse(ctx, path="packages/xowlpost/posts/example.mdx"):
    print(f"🖊️  Signing pulse at {path}")


@task
def export_logbook(ctx):
    sig_dir = Path(".signatures")
    logbook = []
    for sig_file in sig_dir.glob("*.json"):
        try:
            logbook.append(json.loads(sig_file.read_text()))
        except Exception as e:
            print(f"⚠️ Skipped {sig_file.name}: {e}")
    Path("vault.logbook.json").write_text(json.dumps(logbook, indent=2))
    print(f"📖 Wrote vault.logbook.json")
    upload_logbook_to_arweave()


@task(help={"slug": "Slug of the signed pulse (without .mdx)"})
def verify(ctx, slug):
    sig_path = Path(".signatures") / f"{slug}.json"
    post_path = Path("packages/xowlpost/posts") / f"{slug}.mdx"
    if not sig_path.exists() or not post_path.exists():
        print(f"❌ Missing file or signature for: {slug}")
        return
    local_sha = hashlib.sha256(post_path.read_text().encode("utf-8")).hexdigest()
    sig_data = json.loads(sig_path.read_text())
    if sig_data["sha256"] != local_sha:
        print(f"⚠️ SHA mismatch!")
    else:
        print(f"✅ Local SHA verified")
    tx_id = sig_data.get("arweave_tx")
    if tx_id:
        try:
            resp = requests.get(f"https://arweave.net/{tx_id}")
            if resp.status_code == 200 and local_sha in resp.text:
                print(f"⛓️ Arweave TX {tx_id} verified")
            else:
                print(f"⚠️ Arweave mismatch or content not found")
        except Exception as e:
            print(f"❌ Error verifying Arweave: {e}")


@task
def verify_all(ctx):
    sigs = Path(".signatures").glob("*.json")
    for sig_file in sigs:
        slug = Path(json.loads(sig_file.read_text())["file"]).stem
        verify(ctx, slug)


ns = Collection()
ns.add_task(init)
ns.add_task(sign_pulse)
ns.add_task(verify)
ns.add_task(verify_all)
ns.add_task(export_logbook)

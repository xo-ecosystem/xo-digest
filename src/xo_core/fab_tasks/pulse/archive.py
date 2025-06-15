import datetime
import hashlib
import hmac
import json
import os
from pathlib import Path

import requests
from arweave import Transaction, Wallet
from dotenv import load_dotenv
from invoke import Collection, task


@task(
    help={
        "html_preview": "Generate HTML previews before uploading",
        "clear": "Force reupload of already archived pulses",
    }
)
def archive(c, html_preview=False, clear=False):
    """
    📦 Archive pulse to Arweave/IPFS with CID + SHA256 + Signature
    """
    print("📦 Collecting all pulses for archiving...")

    load_dotenv()
    LIGHTHOUSE_API_KEY = os.getenv("LIGHTHOUSE_API_KEY")
    arweave_keyfile = os.getenv("ARWEAVE_KEYFILE")
    if not arweave_keyfile or not Path(arweave_keyfile).expanduser().is_file():
        raise FileNotFoundError(
            f"❌ ARWEAVE_KEYFILE not found or not set: {arweave_keyfile}"
        )
    arweave_wallet = Wallet(str(Path(arweave_keyfile).expanduser().resolve()))

    pulses = list(Path("content/pulses").glob("*.mdx"))
    if not pulses:
        print("⚠️ No pulse files found.")
        return

    signed_dir = Path("vault/.signed")
    signed_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = Path(".preview")
    preview_dir.mkdir(parents=True, exist_ok=True)

    # Load previous manifest
    manifest_path = signed_dir / "pulse_archive_manifest.json"
    old_manifest = {}
    if manifest_path.exists():
        try:
            old_manifest = {
                entry["sha256"]: entry
                for entry in json.loads(manifest_path.read_text())
            }
        except Exception:
            pass

    archive_manifest = []

    for p in pulses:
        content = p.read_text()
        sha256 = hashlib.sha256(content.encode()).hexdigest()

        # Ensure pulse .mdx is saved to vault/.signed/ with correct filename
        try:
            slug_name = f"pulse_{p.stem}.mdx"
            signed_copy_path = signed_dir / slug_name
            signed_copy_path.write_text(content)
        except Exception as e:
            print(f"⚠️ Failed to copy {p.name} to {signed_copy_path}: {e}")

        # Verify file integrity by rehashing the copied file
        try:
            verify_hash = hashlib.sha256(
                signed_copy_path.read_text().encode()
            ).hexdigest()
            if verify_hash != sha256:
                print(
                    f"❌ Integrity check failed for {p.name}: original vs copied hash mismatch"
                )
                continue
        except Exception as e:
            print(f"⚠️ Failed to verify {p.name} in .signed/: {e}")
            continue

        if sha256 in old_manifest and not clear:
            print(f"  🔁 Skipping already archived file: {p.name}")
            archive_manifest.append(old_manifest[sha256])
            continue

        print(f"  ✅ Included in archive: {p.name} — {sha256[:8]}...")

        metadata = {
            "file": p.name,
            "slug": p.stem,
            "sha256": sha256,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
        metadata["local_path"] = slug_name

        try:
            with open(p, "rb") as f:
                response = requests.post(
                    "https://node.lighthouse.storage/api/v0/add",
                    headers={"Authorization": f"Bearer {LIGHTHOUSE_API_KEY}"},
                    files={"file": f},
                )
            cid = response.json()["Hash"] if response.ok else None
            if not cid:
                print(f"⚠️ Lighthouse upload failed: {response.text}")
        except Exception as e:
            print(f"⚠️ Exception during Lighthouse upload: {e}")
            cid = None
        metadata["cid"] = cid

        if html_preview:
            try:
                import markdown

                preview_html = markdown.markdown(content)
                preview_path = preview_dir / f"{p.stem}.html"
                preview_path.write_text(preview_html)
                with open(preview_path, "rb") as f:
                    res = requests.post(
                        "https://node.lighthouse.storage/api/v0/add",
                        headers={"Authorization": f"Bearer {LIGHTHOUSE_API_KEY}"},
                        files={"file": f},
                    )
                preview_cid = res.json()["Hash"] if res.ok else None
                metadata["preview_cid"] = preview_cid
            except Exception as e:
                print(f"⚠️ Failed to generate/upload HTML preview: {e}")
                metadata["preview_cid"] = None

        try:
            tx = Transaction(arweave_wallet, data=content.encode())
            tx.sign()
            tx.send()
            metadata["arweave_txid"] = tx.id
            metadata["arweave_url"] = (
                f"https://viewblock.io/arweave/tx/{tx.id}" if tx.id else None
            )
        except Exception as e:
            print(f"⚠️ Failed to upload to Arweave for {p.name}: {e}")
            metadata["arweave_txid"] = None
            metadata["arweave_url"] = None

        # --- Thirdweb NFT minting logic ---
        try:
            from thirdweb import ThirdwebSDK
            from thirdweb.types.nft import NFTMetadataInput

            thirdweb_key = os.getenv("THIRDWEB_SECRET_KEY")
            contract_address = os.getenv("THIRDWEB_CONTRACT_ADDRESS")
            if not thirdweb_key or not contract_address:
                print("⚠️ Missing Thirdweb API key or contract address.")
            else:
                sdk = ThirdwebSDK.from_private_key(thirdweb_key, "polygon")
                contract = sdk.get_nft_collection(contract_address)

                nft_metadata = NFTMetadataInput(
                    name=p.stem.replace("_", " ").title(),
                    description=f"Pulse Archive: {p.stem}",
                    image=(
                        f"https://gateway.lighthouse.storage/ipfs/{cid}" if cid else ""
                    ),
                    external_url=metadata.get("arweave_url", ""),
                )
                minted = contract.mint(nft_metadata)
                metadata["thirdweb_token_id"] = minted.get("id")
                metadata["thirdweb_url"] = (
                    f"https://thirdweb.com/polygon/{contract_address}/{minted.get('id')}"
                )
                print(f"🪙 Minted NFT: Token ID {minted.get('id')}")
        except Exception as e:
            print(f"⚠️ Failed to mint NFT via Thirdweb: {e}")

        secret_key = os.getenv("VAULT_SECRET_KEY", "changeme").encode()
        signature = hmac.new(
            secret_key, sha256.encode(), digestmod="sha256"
        ).hexdigest()
        metadata["signature"] = signature

        # Ensure thirdweb fields are present before writing
        metadata["thirdweb_token_id"] = metadata.get("thirdweb_token_id")
        metadata["thirdweb_url"] = metadata.get("thirdweb_url")

        (signed_dir / f"{p.stem}.archive.json").write_text(
            json.dumps(metadata, indent=2)
        )

        archive_manifest.append(metadata)

    # Optionally include .signed/index.html in the archive
    index_html = signed_dir / "index.html"
    index_cid = None
    if index_html.exists():
        print(f"🌍 Uploading .signed/index.html to Lighthouse...")
        try:
            with open(index_html, encoding="utf-8") as f:
                index_content = f.read()
            # Modify index_content to update CID links and add Signed badge
            from jinja2 import Template

            template = Template(index_content)

            for entry in archive_manifest:
                entry["local_path"] = entry.get(
                    "local_path", f"pulse_{Path(entry.get('file', '')).stem}.mdx"
                )
                entry["cid_short"] = (
                    (entry.get("cid") or "")[:8] + "…" if entry.get("cid") else ""
                )
                entry["arweave_url"] = entry.get("arweave_url")
                entry["signature"] = entry.get("signature")
                entry["arweave_link"] = (
                    f'<a href="{entry["arweave_url"]}" target="_blank">Arweave</a>'
                    if entry["arweave_url"]
                    else "—"
                )
                entry["signed_badge"] = (
                    "✔ Signed" if entry.get("signature") else "✘ Unsigned"
                )

            rendered_html = template.render(archive_manifest=archive_manifest)

            # Write back the modified index.html
            index_html.write_text(rendered_html, encoding="utf-8")

            with open(index_html, "rb") as f:
                res = requests.post(
                    "https://node.lighthouse.storage/api/v0/add",
                    headers={"Authorization": f"Bearer {LIGHTHOUSE_API_KEY}"},
                    files={"file": f},
                )
            index_cid = res.json()["Hash"] if res.ok else None
            if index_cid:
                print(f"✅ index.html CID: {index_cid}")
                (signed_dir / "index_html.cid").write_text(index_cid)
            else:
                print(f"⚠️ index.html upload failed: {res.text}")
        except Exception as e:
            print(f"⚠️ Exception uploading index.html: {e}")

    # Log HTML preview CIDs
    preview_manifest = [
        {
            "file": Path(m.get("file", "")).name,
            "slug": Path(m.get("file", "")).stem,
            "cid": m.get("cid"),
            "preview_cid": m.get("preview_cid"),
            "title": m.get("file", "").replace("_", " ").replace(".mdx", "").title(),
            "arweave_url": m.get("arweave_url"),
        }
        for m in archive_manifest
        if "preview_cid" in m
    ]
    if index_cid is not None:
        preview_manifest.append(
            {
                "slug": "index_html",
                "file": "index.html",
                "cid": index_cid,
                "preview_cid": None,
                "title": "Pulse Archive Explorer",
                "arweave_url": None,
            }
        )
    preview_manifest_data = {"index_html_cid": index_cid, "entries": preview_manifest}
    (signed_dir / "preview_manifest.json").write_text(
        json.dumps(preview_manifest_data, indent=2)
    )
    manifest_path.write_text(json.dumps(archive_manifest, indent=2))

    # Cleanup preview HTML files after upload
    for f in preview_dir.glob("*.html"):
        try:
            f.unlink()
            print(f"🧹 Removed preview file: {f}")
        except Exception as e:
            print(f"⚠️ Failed to delete {f}: {e}")

    print(f"✅ Archive complete: {len(archive_manifest)} files processed.")
    print(f"📄 Manifest saved: {manifest_path}")


ns = Collection()
ns.add_task(archive, name="run")  # ← This name defines the command suffix

from xo_core.fab_tasks.ipfs import upload_to_ipfs
from xo_core.fab_tasks.pulse.archive import archive as archive_task


# --- Archive relay integration ---
def handle_archive_request():
    from invoke import Context
    ctx = Context()
    archive_task(ctx, slug=None, html_preview=True, clear=False, dry_run=False)

    # --- IPFS stub .mdx generation ---
    from pathlib import Path
    import json

    try:
        manifest_path = Path("vault/.signed/pulse_archive_manifest.json")
        if manifest_path.exists():
            archive_manifest = json.loads(manifest_path.read_text())
            for entry in archive_manifest:
                cid = entry.get("cid")
                if cid:
                    ipfs_stub_path = Path(f"vault/.signed/{entry['slug']}.ipfs.mdx")
                    ipfs_stub_path.write_text(
                        f"# IPFS Entry for {entry['slug']}\n\n"
                        f"CID: `{cid}`\n\n"
                        f"Link: https://ipfs.io/ipfs/{cid}\n"
                    )
                    print(f"🧾 Created IPFS stub: {ipfs_stub_path}")

            # --- Optional: Upload .ipfs.mdx stubs to IPFS and Arweave ---
            from xo_core.fab_tasks.ipfs import upload_to_ipfs
            for entry in archive_manifest:
                cid = entry.get("cid")
                if not cid:
                    continue
                ipfs_stub_path = Path(f"vault/.signed/{entry['slug']}.ipfs.mdx")
                if ipfs_stub_path.exists():
                    try:
                        ipfs_result = upload_to_ipfs(ipfs_stub_path)
                        print(f"📡 Uploaded stub to IPFS: {ipfs_result.get('cid')}")
                    except Exception as e:
                        print(f"⚠️ Failed to upload stub to IPFS: {e}")

        # --- Optional: Upload all other .archive.json files or media to IPFS ---
        try:
            archive_files = list(Path("vault/.signed").glob("*.archive.json"))
            for archive_file in archive_files:
                try:
                    result = upload_to_ipfs(archive_file)
                    print(f"📦 Uploaded archive JSON to IPFS: {result.get('cid')}")
                except Exception as e:
                    print(f"⚠️ Failed to upload archive JSON to IPFS: {e}")
        except Exception as e:
            print(f"⚠️ Failed to gather .archive.json files: {e}")

        # Optional: auto-sync stubs to Vault Explorer if available
        from subprocess import run
        try:
            print("🔁 Syncing to Vault Explorer...")
            run(["xo-fab", "explorer.auto"], check=True)
        except Exception as e:
            print(f"⚠️ explorer.auto sync failed: {e}")

        # Optional: track synced .ipfs.mdx files
        try:
            synced_stubs = list(Path("vault/.signed").glob("*.ipfs.mdx"))
            tracked = [f.name for f in synced_stubs]
            print(f"📁 Synced IPFS stubs: {json.dumps(tracked, indent=2)}")
            (Path("vault/.signed/ipfs_synced.json")).write_text(json.dumps(tracked, indent=2))
        except Exception as e:
            print(f"⚠️ Failed to track synced IPFS stubs: {e}")

        # --- Optional: Track synced .archive.json files too ---
        try:
            synced_archives = list(Path("vault/.signed").glob("*.archive.json"))
            tracked_archives = [f.name for f in synced_archives]
            print(f"📁 Synced Archive JSONs: {json.dumps(tracked_archives, indent=2)}")
            (Path("vault/.signed/archive_synced.json")).write_text(json.dumps(tracked_archives, indent=2))
        except Exception as e:
            print(f"⚠️ Failed to track synced archive JSONs: {e}")
    except Exception as e:
        print(f"⚠️ Failed to generate .ipfs.mdx stubs: {e}")

    # --- Optional: Upload preview_manifest.ipfs.mdx to IPFS and Arweave ---
    try:
        from pathlib import Path
        preview_stub = Path("vault/.signed/preview_manifest.ipfs.mdx")
        if preview_stub.exists():
            result = upload_to_ipfs(preview_stub)
            print(f"🌐 Uploaded preview manifest to IPFS: {result.get('cid')}")
            # Save result as /vault/daily/preview_manifest.mdx
            vault_daily_path = Path("vault/daily")
            vault_daily_path.mkdir(parents=True, exist_ok=True)
            output_path = vault_daily_path / "preview_manifest.mdx"
            output_path.write_text(preview_stub.read_text())
            print(f"🗂️ Written to: {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to upload preview manifest or write to daily view: {e}")

    # --- Optional: Render /vault/daily/index.html ---
    try:
        from jinja2 import Template
        index_template_path = Path("vault/daily/template.html")
        output_index_path = Path("vault/daily/index.html")
        if index_template_path.exists():
            tmpl = Template(index_template_path.read_text())
            synced = json.loads(Path("vault/.signed/ipfs_synced.json").read_text())
            entries = []
            for name in synced:
                entry = {}
                if name.endswith(".ipfs.mdx"):
                    entry["type"] = "ipfs"
                    entry["slug"] = name.replace(".ipfs.mdx", "")
                elif name.endswith(".archive.json"):
                    entry["type"] = "archive"
                    entry["slug"] = name.replace(".archive.json", "")
                else:
                    continue
                # Add synced field based on .ipfs.sync file existence
                from pathlib import Path
                sync_file = Path("vault/.signed") / f"{entry['slug']}.ipfs.sync"
                if sync_file.exists():
                    entry["synced"] = True
                else:
                    entry["synced"] = False
                entries.append(entry)
            rendered = tmpl.render(entries=entries)
            output_index_path.write_text(rendered)
            print(f"📄 Rendered /vault/daily/index.html with {len(entries)} entries")
            try:
                # Auto-copy rendered index.html to xoledger.com vault view (e.g., GitHub Pages folder)
                import shutil
                mirror_path = Path("public/vault/daily/index.html")
                mirror_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(output_index_path, mirror_path)
                print(f"🔁 Mirrored index.html to {mirror_path}")
            except Exception as e:
                print(f"⚠️ Failed to mirror to xoledger.com: {e}")
        else:
            print("⚠️ No template found at /vault/daily/template.html")
    except Exception as e:
        print(f"⚠️ Failed to render /vault/daily/index.html: {e}")
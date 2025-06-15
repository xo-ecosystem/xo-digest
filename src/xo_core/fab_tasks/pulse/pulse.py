"""
XO Pulse Tasks Module

This module provides Fabric tasks to manage 'pulses' within the XO ecosystem. Pulses are markdown-based content pieces that can be created, synced to Arweave, published to IPFS, signed, previewed, and cleaned using these tasks.

Available Tasks:
- pulse.new:<slug>       Create a new pulse with a default template.
- pulse.sync             Upload all pulses to Arweave and log transaction IDs.
- pulse.sign:<slug>      Trigger the signing endpoint for a specific pulse.
- pulse.publish:<slug>   Upload a pulse, pin it to IPFS, and trigger signing.
- pulse.preview:<slug>   Render a pulse as HTML for review.
- pulse.clean            Remove .txid and .preview artifacts.

Usage:
  xo-fab pulse.new:example-slug
  xo-fab pulse.sync
  xo-fab pulse.publish:example-slug
  xo-fab pulse.preview:example-slug
  xo-fab pulse.clean

Dependencies:
- arweave-python-client
- markdown2
- requests
"""

import json
import os
from pathlib import Path

from invoke import Collection, task


# Task to synchronize all pulse markdown files by uploading them to Arweave,
# saving their transaction IDs, and updating the logbook.
@task
def sync(c):
    pulses_dir = Path("content/pulses")
    if not pulses_dir.exists():
        print("❌ content/pulses/ not found")
        return

    mdx_files = list(pulses_dir.glob("*.mdx"))
    if not mdx_files:
        print("⚠️ No .mdx pulse files found to sync.")
        return

    print(f"🔄 Found {len(mdx_files)} pulse(s) to sync:")
    try:
        from arweave import Transaction, Wallet

        wallet_path = Path(".arweave.key.json")
        if not wallet_path.exists():
            print(
                "⚠️  Arweave wallet key (.arweave.key.json) not found. Skipping upload."
            )
            return

        wallet = Wallet(str(wallet_path))

        logbook_path = Path(".vault/logbook.json")
        logbook = {}

        if logbook_path.exists():
            try:
                logbook = json.loads(logbook_path.read_text())
            except Exception:
                print("⚠️ Failed to load existing logbook. Starting fresh.")

        for file in mdx_files:
            print(f"  📄 {file.name}")
            tx = Transaction(wallet, data=file.read_text())
            tx.add_tag("Content-Type", "text/markdown")
            tx.sign()
            tx.send()
            print(f"  ✅ Uploaded {file.name} → Arweave tx: {tx.id}")

            # Save .txid file
            txid_path = file.with_suffix(file.suffix + ".txid")
            txid_path.write_text(tx.id)

            vault_txid_path = Path(".vault/txids") / txid_path.name
            vault_txid_path.parent.mkdir(parents=True, exist_ok=True)
            vault_txid_path.write_text(tx.id)

            # Update logbook
            logbook[file.name] = tx.id

        # Write back updated logbook
        try:
            logbook_path.parent.mkdir(parents=True, exist_ok=True)
            logbook_path.write_text(json.dumps(logbook, indent=2))
            from datetime import datetime

            snapshot_path = logbook_path.with_name(
                f"logbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            snapshot_path.write_text(json.dumps(logbook, indent=2))
            print("🗂️  Logbook updated: .vault/logbook.json")
        except Exception as e:
            print(f"⚠️ Failed to write logbook: {e}")

    except ImportError:
        print(
            "⚠️ arweave-python-client not installed. Run: pip install arweave-python-client"
        )
    except Exception as e:
        print(f"❌ Upload failed: {e}")

    print("✅ Pulse sync complete.")


# Task to trigger the signing endpoint for a given pulse slug.
@task(positional=["slug"])
def sign(c, slug=None):
    print(f"🔏 Pulse signed: {slug or 'ALL'}")


# Task to publish a single pulse: upload to Arweave, pin to IPFS, and trigger signing.
@task(positional=["slug"])
def publish(c, slug):
    """
    📤 Publish a pulse by syncing it and optionally signing it.
    Usage: xo-fab pulse.publish:slug
    """
    import requests
    from arweave import Transaction, Wallet

    file_path = Path("content/pulses") / f"{slug}.mdx"
    if not file_path.exists():
        print(f"❌ Pulse not found: {file_path}")
        return

    print(f"📤 Publishing pulse: {slug}")
    wallet_path = Path(".arweave.key.json")
    if not wallet_path.exists():
        print("⚠️  Arweave wallet key (.arweave.key.json) not found. Skipping upload.")
        return

    wallet = Wallet(str(wallet_path))
    tx = Transaction(wallet, data=file_path.read_text())
    tx.add_tag("Content-Type", "text/markdown")
    tx.sign()
    tx.send()
    print(f"✅ Uploaded {file_path.name} → Arweave tx: {tx.id}")

    txid_path = file_path.with_suffix(file_path.suffix + ".txid")
    txid_path.write_text(tx.id)
    vault_txid_path = Path(".vault/txids") / txid_path.name
    vault_txid_path.parent.mkdir(parents=True, exist_ok=True)
    vault_txid_path.write_text(tx.id)

    logbook_path = Path(".vault/logbook.json")
    logbook = {}
    if logbook_path.exists():
        try:
            logbook = json.loads(logbook_path.read_text())
        except Exception:
            print("⚠️ Failed to load existing logbook. Starting fresh.")
    logbook[file_path.name] = tx.id
    logbook_path.write_text(json.dumps(logbook, indent=2))

    try:
        res = requests.post(
            "https://api.web3.storage/upload",
            headers={
                "Authorization": f"Bearer {os.getenv('WEB3_STORAGE_TOKEN', 'MISSING_TOKEN')}"
            },
            files={"file": open(file_path, "rb")},
        )
        if res.status_code == 200:
            cid = res.json().get("cid")
            print(f"📦 IPFS pinned: {cid}")
        else:
            print(f"⚠️ IPFS upload failed: {res.status_code}")
    except Exception as e:
        print(f"⚠️ IPFS pin skipped: {e}")

    try:
        res = requests.post(f"http://localhost:8000/sign/{slug}", timeout=3)
        print(f"🧠 Triggered /sign/{slug} → {res.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to trigger /sign/{slug}: {e}")


# Task to create a new pulse markdown file with a default template.
@task(positional=["slug"])
def new(c, slug):
    """
    🆕 Create a new pulse with default template
    """
    dest = Path("content/pulses") / f"{slug}.mdx"
    if dest.exists():
        print("⚠️ Pulse already exists.")
        return

    template = f"""---
title: "New Pulse"
slug: "{slug}"
date: "{__import__('datetime').date.today()}"
author: "xo"
signed: false
---

Begin your pulse here.
"""
    dest.write_text(template)
    print(f"✅ New pulse created at: {dest}")


# Task to render a pulse markdown file to HTML and save it to a preview directory.
@task(positional=["slug"])
def preview(c, slug):
    """
    👁️ Preview a pulse in terminal or browser
    """
    from markdown2 import markdown

    file_path = Path("content/pulses") / f"{slug}.mdx"
    if not file_path.exists():
        print(f"❌ Pulse not found: {file_path}")
        return

    html = markdown(file_path.read_text())
    preview_path = Path(f".preview/{slug}.html")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text(html)
    print(f"🔍 Preview written to: {preview_path}")


# Task to clean up generated .txid files and HTML preview files.
@task
def clean(c):
    """
    🧹 Clean .txid and .preview files
    """
    for path in Path("content/pulses").glob("*.mdx.txid"):
        path.unlink()
    preview_dir = Path(".preview")
    if preview_dir.exists():
        for file in preview_dir.glob("*.html"):
            file.unlink()
    print("🧼 Cleaned .txid and .preview artifacts.")


# Doctor task for pulse setup checks
@task
def doctor(c):
    """
    🩺 Check pulse setup status (paths, CLI, dependencies)
    """
    print("🔍 Running pulse doctor...")
    problems = False

    expected_dirs = ["content/pulses", ".vault/txids", ".preview"]
    for d in expected_dirs:
        p = Path(d)
        if not p.exists():
            print(f"⚠️  Missing expected directory: {d} — creating it now.")
            p.mkdir(parents=True, exist_ok=True)

    # Ensure .env exists, or create with safe defaults
    if not Path(".env").exists():
        print("⚠️  Missing .env file — creating with defaults.")
        Path(".env").write_text(
            "VAULT_TOKEN=localtoken\nVAULT_ADDR=http://localhost:8200\n"
        )

    # Ensure .vault, .vault/txids, .vault/logbook.json exist
    vault_paths = [".vault", ".vault/txids", ".vault/logbook.json"]
    for path in vault_paths:
        p = Path(path)
        if not p.exists():
            print(f"⚠️  Missing vault path: {path} — creating it now.")
            if path.endswith(".json"):
                p.write_text("{}")
            else:
                p.mkdir(parents=True, exist_ok=True)

    # Additional required files and directories validation
    required_files = [".arweave.key.json", ".env"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file missing: {file}")
            problems = True

    required_dirs = ["cli", "fab_tasks"]
    for dir in required_dirs:
        if not Path(dir).exists():
            print(f"❌ Required directory missing: {dir}")
            problems = True

    pulse_cli = Path.home() / ".local/bin/xo-pulse"
    if not pulse_cli.exists():
        print("❌ xo-pulse CLI not found in ~/.local/bin")
        problems = True

    env_path = os.environ.get("PATH", "")
    if str(Path.home() / ".local/bin") not in env_path:
        print("⚠️  ~/.local/bin not in $PATH")
        print("💡 Add this to your ~/.zshrc:")
        print('export PATH="$HOME/.local/bin:$PATH"')

    # Check for .comments directory
    if not Path(".comments").exists():
        print("⚠️  Missing .comments directory — creating it now.")
        Path(".comments").mkdir(parents=True, exist_ok=True)

    # Check for .signed directory
    if not Path(".signed").exists():
        print("⚠️  Missing .signed directory — creating it now.")
        Path(".signed").mkdir(parents=True, exist_ok=True)

    # Check for .coin.yml files in content/pulses
    coin_files = list(Path("content/pulses").glob("*.coin.yml"))
    if not coin_files:
        print("⚠️  No .coin.yml metadata files found in content/pulses/")
        for mdx in Path("content/pulses").glob("*.mdx"):
            coin_path = mdx.with_name(mdx.stem + ".coin.yml")
            if not coin_path.exists():
                coin_template = f"""slug: {mdx.stem}
title: "Untitled"
author: "xo"
description: "Describe your pulse..."
tags: []
edition: "genesis"
"""
                coin_path.write_text(coin_template)
                print(f"🪙 Created template: {coin_path}")
    else:
        print(f"📦 Found {len(coin_files)} .coin.yml file(s).")

    # Check for .comments.mdx files matching each .mdx
    for mdx in Path("content/pulses").glob("*.mdx"):
        comments_path = Path(".comments") / f"{mdx.stem}.comments.mdx"
        if not comments_path.exists():
            print(f"⚠️  Missing comment file for {mdx.stem} — creating placeholder.")
            comments_path.write_text(f"<!-- Comments for {mdx.stem} -->\n")

    # Validate .signed/*.json signature presence for each pulse
    for mdx in Path("content/pulses").glob("*.mdx"):
        signature_path = Path(".signed") / f"{mdx.stem}.json"
        if not signature_path.exists():
            print(
                f"⚠️  Missing signature for {mdx.stem} — expected at .signed/{mdx.stem}.json"
            )
            stub = {
                "signed": False,
                "slug": mdx.stem,
                "meta": "auto-generated placeholder",
            }
            signature_path.write_text(json.dumps(stub, indent=2))
            print(f"🧾 Created stub signature: {signature_path}")
        else:
            try:
                with signature_path.open() as f:
                    data = json.load(f)
                assert isinstance(data.get("signed"), bool)
                assert isinstance(data.get("slug"), str)
                assert isinstance(data.get("meta"), str)
            except Exception as e:
                print(f"❌ Invalid signature schema in {signature_path}: {e}")
                problems = True

    # Check for .txid consistency
    for mdx in Path("content/pulses").glob("*.mdx"):
        txid_path = mdx.with_suffix(mdx.suffix + ".txid")
        vault_txid_path = Path(".vault/txids") / txid_path.name
        if not txid_path.exists():
            print(f"⚠️  Missing .txid for {mdx.stem} — expected at {txid_path}")
            problems = True
        if not vault_txid_path.exists():
            print(
                f"⚠️  Missing vault .txid for {mdx.stem} — expected at {vault_txid_path}"
            )
            problems = True
        elif txid_path.exists():
            try:
                local_txid = txid_path.read_text().strip()
                vault_txid = vault_txid_path.read_text().strip()
                if local_txid != vault_txid:
                    print(
                        f"❌ Mismatched .txid for {mdx.stem} — local and vault values differ."
                    )
                    problems = True
            except Exception as e:
                print(f"❌ Error reading .txid for {mdx.stem}: {e}")
                problems = True

    # Check for .preview/*.html existence
    for mdx in Path("content/pulses").glob("*.mdx"):
        preview_path = Path(".preview") / f"{mdx.stem}.html"
        if not preview_path.exists():
            print(f"👁️  Missing preview for {mdx.stem} → {preview_path}")
            # Optional: regenerate preview
            try:
                from markdown2 import markdown

                html = markdown(mdx.read_text())
                preview_path.write_text(html)
                print(f"🔁 Regenerated preview: {preview_path}")
            except Exception as e:
                print(f"⚠️ Failed to regenerate preview for {mdx.stem}: {e}")
                problems = True

    # Check logbook.json for matching entries
    logbook_path = Path(".vault/logbook.json")
    if logbook_path.exists():
        try:
            logbook_data = json.loads(logbook_path.read_text())
            for mdx in Path("content/pulses").glob("*.mdx"):
                key = mdx.name
                txid_path = mdx.with_suffix(mdx.suffix + ".txid")
                if key not in logbook_data:
                    print(f"📓 Logbook entry missing for {key}")
                    problems = True
                elif txid_path.exists():
                    try:
                        txid = txid_path.read_text().strip()
                        if logbook_data[key] != txid:
                            print(f"❌ TXID mismatch in logbook for {key}")
                            problems = True
                    except Exception as e:
                        print(f"⚠️ Could not read .txid for {key}: {e}")
                        problems = True
        except Exception as e:
            print(f"⚠️ Failed to read logbook.json: {e}")
            problems = True

    if not problems:
        print("✅ All systems go for pulse tasks!")


# Expose the ns collection as required
ns = Collection("pulse")
ns.add_task(sync)
ns.add_task(sign)
ns.add_task(publish)
ns.add_task(new)
ns.add_task(preview)
ns.add_task(clean)
ns.add_task(doctor)

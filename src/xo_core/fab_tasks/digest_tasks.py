import os
import subprocess
from datetime import date as dt_date
from pathlib import Path

from invoke import Collection, task

from xo_core.utils.digest import create_digest_zip


@task
def digest_notify(
    c,
    date=None,
    zip=False,
    push=False,
    commit=False,
    duration=None,
    no_arweave=False,
    no_ipfs=False,
):
    """📬 Notify Telegram & Discord of the latest digest (optionally zipped). Use --no-arweave and --no-ipfs to skip uploads."""
    import json
    from datetime import datetime

    if not date:
        files = sorted(Path("vault/daily").glob("*.slim.md"), reverse=True)
        if not files:
            raise ValueError("❌ No digest files found in vault/daily/")
        date = files[0].stem.split(".")[0]
    today = date
    vault_path = Path("vault/daily")
    zip_path = None

    # Ensure .slim.md exists for today, auto-render if missing
    slim_md_path = Path(f"vault/daily/{today}.slim.md")
    if not slim_md_path.exists():
        print(f"⚠️ {slim_md_path} not found, auto-rendering slim digest...")
        c.run(f"xo-fab vault.digest.render --slim --date={today}")

    md_link = f"https://xo-digest.pages.dev/vault/daily/{today}.slim.md"
    html_link = "https://xo-digest.pages.dev/vault/daily/index.html"
    bundle_link = f"https://xo-digest.pages.dev/vault/daily/{today}.zip"

    if zip:
        zip_path = create_digest_zip(today)
        print(f"📦 Created digest zip: {zip_path}")
        if not no_arweave:
            if Path("scripts/upload_to_arweave.sh").exists():
                print("📡 Uploading .zip to Arweave...")
                result = c.run(
                    f"bash scripts/upload_to_arweave.sh {zip_path}",
                    warn=True,
                    hide=True,
                )
                if result.failed:
                    print(f"❌ Arweave upload failed:\n{result.stderr}")
            else:
                print("⚠️ Arweave upload script not found, skipping.")
        if not no_ipfs:
            if Path("scripts/pin_to_ipfs.sh").exists():
                print("📡 Pinning to IPFS...")
                result = c.run(
                    f"bash scripts/pin_to_ipfs.sh {zip_path}", warn=True, hide=True
                )
                if result.failed:
                    print(f"❌ IPFS pinning failed:\n{result.stderr}")

        if commit:
            print("📦 Committing digest files to Git...")
            c.run("git config user.name 'xo-ci-bot'")
            c.run("git config user.email 'bot@xopipeline.local'")
            md_file = f"vault/daily/{today}.md"
            slim_file = f"vault/daily/{today}.slim.md"
            zip_file = f"vault/daily/{today}.zip"
            html_file = f"vault/daily/index.html"
            tracked = [md_file, slim_file, zip_file]
            if Path(html_file).exists():
                tracked.append(html_file)
            precommit_config = Path(".pre-commit-config.yaml")
            if precommit_config.exists():
                tracked.append(str(precommit_config))
            c.run(f"git add {' '.join(tracked)}")
            c.run(f"git commit -m '📦 Digest for {today}' || echo 'No changes'")
            c.run("git push || echo 'No push needed'")

    if not commit:
        commit = c.run("git rev-parse --short HEAD", hide=True).stdout.strip()
    if not duration:
        duration = "⏱️ Duration: unknown"
    else:
        duration = f"⏱️ Duration: {duration}"

    msg = f"""📬 XO Vault Digest – {today}

🔗 [Live Digest]({html_link})
📎 [Slim .md]({md_link})"""
    if zip:
        msg += f"\n📦 [Bundle .zip]({bundle_link})"

        arweave_tx_path = Path("arweave_tx.txt")
        ipfs_cid_path = Path("ipfs_cid.txt")
        if arweave_tx_path.exists():
            tx_id = arweave_tx_path.read_text().strip()
            msg += f"\n\n🌐 [Arweave Link](https://arweave.net/{tx_id})"
        if ipfs_cid_path.exists():
            cid = ipfs_cid_path.read_text().strip()
            msg += f"\n🧬 [IPFS CID](ipfs://{cid})"

    msg += f"\n\n🧬 Commit: {commit}\n{duration}"

    if push:
        telegram_url = os.environ.get("XO_TELEGRAM_WEBHOOK")
        discord_url = os.environ.get("XO_DISCORD_WEBHOOK")
        payload = {"content": msg}
        payload_json = json.dumps(payload)

        if telegram_url:
            c.run(
                f"curl -s -X POST -H 'Content-Type: application/json' -d '{payload_json}' {telegram_url}"
            )
        if discord_url:
            c.run(
                f"curl -s -X POST -H 'Content-Type: application/json' -d '{payload_json}' {discord_url}"
            )

    print("✅ Digest notification ready.")


@task
def digest_generate(c, date=None):
    from datetime import date as dt_date

    """📄 Generate today's digest Markdown file."""
    today = date or dt_date.today().isoformat()
    out_path = Path(f"vault/daily/{today}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"📝 Writing digest to {out_path}...")
    out_path.write_text(f"# Daily Digest — {today}\n\n- Placeholder content.\n")


@task
def digest_push(c, commit=False, upload=True):
    """🧠 Full digest flow: generate, sign, upload, commit."""
    today = dt_date.today().isoformat()
    digest_md = f"vault/daily/{today}.md"
    signed_log = f"vault/digests/daily_digest_{today}.log.signed"

    # Step 1: Generate digest
    print("🧪 Generating daily digest...")
    c.run(f"xo-fab vault.digest-generate")

    # Step 2: Sign
    print("🔏 Signing digest log...")
    c.run(f"xo-fab vault.sign:vault/digests/daily_digest_{today}.log")

    # Step 3: Upload to Arweave (if available)
    if upload:
        if Path("scripts/upload_to_arweave.sh").exists():
            print("📤 Uploading to Arweave...")
            try:
                c.run(f"bash scripts/upload_to_arweave.sh {signed_log}")
            except Exception as e:
                print(f"⚠️ Upload failed: {e}")
        else:
            print("⚠️ Arweave upload script not found, skipping.")

    # Step 4: Optional Git commit
    if commit:
        print("📦 Committing digest summary...")
        c.run("git config user.name 'xo-ci-bot'")
        c.run("git config user.email 'bot@xopipeline.local'")
        c.run(f"git add {digest_md} {signed_log}")
        c.run(f"git commit -m '📄 Auto-digest for {today}' || echo 'No changes'")
        c.run("git push || echo 'No push needed'")


@task
def digest_render(
    c, theme="light", tag=None, slim=False, html=False, preview=False, date=None
):
    """🎨 Render digest with optional theme, tag filter, and slim mode."""
    today = date or dt_date.today().isoformat()
    source = Path(f"vault/daily/{today}.md")
    output = Path(f"vault/daily/{today}.rendered.md")
    if slim:
        output = Path(f"vault/daily/{today}.slim.md")

    if not source.exists():
        print(f"❌ Digest not found: {source}")
        return

    lines = source.read_text().splitlines()
    filtered = []

    for line in lines:
        if tag:
            if tag.lower() in line.lower():
                filtered.append(line)
        else:
            filtered.append(line)

    if slim:
        # Keep only lines that look like bullet points or headlines
        filtered = [l for l in filtered if l.startswith("- ") or l.startswith("#")]

    # Apply theme styling (placeholder)
    if theme == "dark":
        filtered.insert(0, "<!-- theme: dark -->")
    else:
        filtered.insert(0, "<!-- theme: light -->")

    output.write_text("\n".join(filtered))
    print(f"✅ Rendered digest saved to {output}")

    if html:
        try:
            from markdown2 import markdown

            html_path = Path(f"vault/daily/{today}.html")
            html_content = markdown("\n".join(filtered))
            html_path.write_text(html_content)
            print(f"🌐 HTML version saved to {html_path}")
            if preview:
                import webbrowser

                webbrowser.open(f"file://{html_path.resolve()}")
        except ImportError:
            print(
                "⚠️ markdown2 module not found. Run `pip install markdown2` to enable HTML rendering."
            )


@task
def digest_preview(c):
    """🌐 Generate styled HTML preview at /vault/daily/index.html from the latest digest .md"""
    today = dt_date.today().isoformat()
    source = Path(f"vault/daily/{today}.md")
    if not source.exists():
        print(f"❌ No digest found at {source}")
        return

    lines = source.read_text().splitlines()
    filtered = [l for l in lines if l.startswith("- ") or l.startswith("#")]
    filtered.insert(0, "<!-- theme: light -->")

    try:
        from markdown2 import markdown

        html_content = markdown("\n".join(filtered))
        output = Path("vault/daily/index.html")
        output.write_text(html_content)
        print(f"✅ Digest HTML preview saved to {output}")
    except ImportError:
        print(
            "⚠️ markdown2 module not found. Run `pip install markdown2` to enable HTML preview."
        )


ns = Collection()
ns.add_task(digest_generate, name="generate")
ns.add_task(digest_push, name="push")
ns.add_task(digest_render, name="render")
ns.add_task(digest_preview, name="preview")
ns.add_task(digest_notify, name="notify")

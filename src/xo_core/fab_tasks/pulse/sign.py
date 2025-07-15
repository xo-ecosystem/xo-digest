from xo_core.fab_tasks.pulse.thirdweb_mint import post_sign_hook
from xo_core.fab_tasks.ipfs import pin_to_ipfs
from xo_core.fab_tasks.vault.digest import update_digest
from invoke import task
from pathlib import Path
from .new import new_pulse
import hashlib

@task(help={
    "slug": "Slug name of the pulse to sign",
    "dry_run": "Only simulate signing, don’t write to file",
    "dry-run": "Only simulate signing, don’t write to file"
})
def sign(c, slug, dry_run=False, **kwargs):
    # Accept both --dry_run and --dry-run
    if not dry_run and kwargs.get("dry-run"):
        dry_run = kwargs["dry-run"]
    """
    🔏 Simulate signing a pulse by writing a .signed file and printing a success message.
    """
    if slug == "test_pulse":
        new_pulse(c, slug=slug)

    pulse_path = Path(f"content/pulses/{slug}/{slug}.mdx")
    signed_dir = Path("vault/.signed")
    signed_dir.mkdir(parents=True, exist_ok=True)

    if not pulse_path.exists():
        print(f"❌ Pulse not found: {pulse_path}")
        return

    content = pulse_path.read_text()
    signature = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
    signed_path = signed_dir / f"{slug}.signed"

    if dry_run:
        print(f"🧪 [dry-run] Would sign: {slug} (would write to {signed_path})")
        print(f"🧪 [dry-run] Signature: {signature}")
        return

    signed_path.write_text(signature)
    print(f"🔏 Pulse signed: {slug}")

    post_sign_hook(c, signed_path)
    pin_to_ipfs(c, path=signed_path)
    update_digest(c, slug)

@task(help={
    "slugs": "Comma-separated slugs of pulses to sign in batch",
    "hook": "Optional: trigger 'ens', 'arweave', or 'digest' after signing"
})
def sign_batch(c, slugs, hook=None):
    """
    🔏 Batch sign multiple pulses by slug with optional post-signing hooks.
    """
    signed_paths = []

    for slug in slugs.split(","):
        slug = slug.strip()
        if not slug:
            continue
        print(f"➡️ Signing: {slug}")
        sign(c, slug)
        signed_path = Path(f"vault/.signed/{slug}.signed")
        if signed_path.exists():
            signed_paths.append(signed_path)

    if hook == "digest":
        for slug in slugs.split(","):
            slug = slug.strip()
            if slug:
                update_digest(c, slug)
        print("📒 Digest updated.")

    elif hook == "arweave":
        from xo_core.fab_tasks.arweave import push_to_arweave
        for path in signed_paths:
            push_to_arweave(c, path)
        print("⛓️ Pushed to Arweave.")

    elif hook == "ens":
        from xo_core.fab_tasks.ens import register_ens
        for slug in slugs.split(","):
            slug = slug.strip()
            if slug:
                register_ens(c, slug)
        print("🌐 ENS registration triggered.")

from invoke import Collection

ns = Collection(sign, sign_batch)
from invoke import task
import os
from pathlib import Path
from rich import print


@task
def sync(c, bundle):
    """
    Sync .mdx files from public/vault/daily/<bundle>/ to content/pulses/
    """
    src_dir = Path(f"public/vault/daily/{bundle}")
    dest_dir = Path("content/pulses")

    if not src_dir.exists():
        print(f"[red]❌ Source bundle not found: {src_dir}[/red]")
        return

    mdx_files = list(src_dir.glob("*.mdx"))
    if not mdx_files:
        print(f"[yellow]⚠️ No .mdx files found in: {src_dir}[/yellow]")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)

    for file in mdx_files:
        target = dest_dir / file.name
        content = file.read_text()
        if not content.strip():
            print(f"[yellow]⚠️ Skipped empty file: {file.name}[/yellow]")
            continue
        target.write_text(content)
        print(f"[green]✅ Synced:[/green] {file.name} → [blue]{target}[/blue]")

    print(f"[cyan]📁 Synced bundle:[/cyan] {bundle}")
    preview_dir = Path(f"public/vault/previews/{bundle}")
    bundle_dir = Path(f"public/vault/bundles/{bundle}")
    if not preview_dir.exists():
        c.run(f"xo-fab pulse.preview:{bundle}", warn=True)
    else:
        print(f"[grey]ℹ️ Skipping pulse.preview — already exists for {bundle}[/grey]")

    if not bundle_dir.exists():
        c.run(f"xo-fab vault.bundle:{bundle}", warn=True)
    else:
        print(f"[grey]ℹ️ Skipping vault.bundle — already exists for {bundle}[/grey]")


# Placeholder task to demonstrate secondary functionality or test loading.
@task
def placeholder(c):
    """
    Placeholder task to demonstrate secondary functionality or test loading.
    """
    print("[grey]ℹ️ Placeholder task executed (vault_pulse_sync)[/grey]")


from invoke import Collection

ns = Collection()
ns.add_task(sync, name="sync")
ns.add_task(placeholder, name="placeholder")

vault_pulse_sync_ns = ns

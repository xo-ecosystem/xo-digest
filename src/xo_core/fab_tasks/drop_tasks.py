from invoke import Collection
from invoke import Context, task
from invoke import task
import shutil
from pathlib import Path

@task
def bundle(ctx, name="first_flip_teaser", sync=False):
    """Create a ZIP bundle of a drop and optionally pin to IPFS."""
    src = Path("vault/drops") / name
    dst = Path("dist") / f"{name}.zip"
    dst.parent.mkdir(exist_ok=True)
    if dst.exists():
        dst.unlink()
    shutil.make_archive(dst.with_suffix(""), "zip", root_dir=src)
    print(f"✅ Bundle ready: {dst}")

    if sync:
        print(f"📡 Pinning bundle to IPFS...")
        ctx.run(f"xo-fab ipfs.sync --path={dst}", pty=True)
    
@task
def generate(c, slug):
    """Scaffold a new drop variant inside xo-drops."""
    c.run(f"python xo-drops/scripts/drop_generate.py {slug}")

ns = Collection("drop")
ns.add_task(bundle, name="bundle")
ns.add_task(generate, name="generate")

__all__ = ["ns"]

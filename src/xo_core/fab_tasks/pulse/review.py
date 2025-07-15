

from invoke import task
from pathlib import Path

@task
def review_pulse(c, slug="test_pulse", dry_run=False):
    """
    Review a signed pulse before publishing.
    Checks for .mdx and .coin.yml presence and shows a summary preview.
    """
    base_path = Path("content/pulses") / slug
    mdx_file = base_path / f"{slug}.mdx"
    coin_file = base_path / f"{slug}.coin.yml"

    if not mdx_file.exists():
        print(f"❌ Missing MDX file: {mdx_file}")
        return

    print(f"📄 Reviewing pulse: {slug}")
    print(f"  - MDX: {'✅' if mdx_file.exists() else '❌'}")
    print(f"  - Coin: {'✅' if coin_file.exists() else '⚠️ Missing'}")

    if dry_run:
        print("ℹ️ Dry run enabled — not modifying or publishing anything.")
    else:
        print("✅ Ready for final publication or preview rendering.")

from invoke import Collection

ns = Collection()
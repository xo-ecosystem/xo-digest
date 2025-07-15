from invoke import Collection, task

@task
def all_with_link(c):
    """
    🔗 Dummy inbox task to ensure namespace loads.
    """
    print("📬 Inbox task executed: all_with_link")

from invoke import task

@task
def all_with_files(c, slug=None):
    """
    Collect all markdown + preview + .ipfs.mdx for a given slug.
    """
    from pathlib import Path
    base = Path("vault")
    files = [
        base / ".signed" / f"{slug}.ipfs.mdx",
        base / ".preview" / f"{slug}.html",
        base / "daily" / f"{slug}.preview.html"
    ]
    for f in files:
        if f.exists():
            print(f"✅ Found: {f}")
        else:
            print(f"❌ Missing: {f}")

ns = Collection("inbox")
ns.add_task(all_with_link, "all_with_link")
ns.add_task(all_with_files, "all_with_files")

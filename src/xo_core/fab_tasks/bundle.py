from invoke import task, Collection
import zipfile
from pathlib import Path

@task
def bundle_sync(c, output="vault/bundle/bundle.zip"):
    """
    📦 Zip all .mdx, .signed, .txid files in vault/ and content/pulses/ into a bundle.zip
    """
    # Get project root (3 levels up from this file: src/xo_core/fab_tasks/bundle.py)
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    
    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define search paths relative to project root
    search_paths = [
        project_root / "vault" / ".signed",
        project_root / "vault" / ".txid", 
        project_root / "vault" / ".preview",
        project_root / "vault" / ".synced",
        project_root / "content" / "pulses"
    ]
    
    files = []
    for search_path in search_paths:
        if not search_path.exists():
            continue
        for ext in ("*.mdx", "*.signed", "*.txid"):
            files.extend(search_path.rglob(ext))
    
    if not files:
        print("❌ No files found to bundle.")
        return
    
    with zipfile.ZipFile(output_path, "w") as zf:
        for file_path in files:
            # Calculate relative path from project root
            try:
                relative_path = file_path.relative_to(project_root)
                zf.write(file_path, relative_path)
                print(f"✅ Added: {relative_path}")
            except ValueError as e:
                print(f"⚠️ Skipping {file_path}: {e}")
                continue
    
    # Get zip file size in KB
    zip_size_kb = output_path.stat().st_size / 1024
    
    print(f"\n📦 Bundle created: {output_path}")
    print(f"📊 Files added: {len(files)}")
    print(f"💾 Size: {zip_size_kb:.1f} KB")

ns = Collection("bundle")
ns.add_task(bundle_sync) 
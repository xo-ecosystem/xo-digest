"""XO Preview Module: Generate preview files for drop bundles."""

from invoke import task, Collection
from pathlib import Path
import shutil
import webbrowser
import os
import yaml
import json

@task(help={"drop": "Name of the drop bundle", "open": "Open the preview folder after generation"})
def generate(c, drop="eighth_seal_3d", open=False):
    """🔍 Generate preview files for a specific drop."""
    print(f"🔍 Generating preview for drop: {drop}")
    
    # Source and destination paths
    src = Path(f"src/xo_core/vault/seals/eighth/drop.assets/{drop}/metadata")
    dst = Path(f"public/vault/previews/{drop}")
    
    if not src.exists():
        print(f"❌ Source path not found: {src}")
        return False
    
    # Create destination directory
    dst.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    copied_files = []
    
    # Copy webp files
    for webp_file in src.glob("*.webp"):
        shutil.copy2(webp_file, dst / webp_file.name)
        copied_files.append(webp_file.name)
        print(f"  ✅ Copied: {webp_file.name}")
    
    # Copy metadata files
    for meta_file in ["drop.preview.yml", "drop.status.json"]:
        meta_path = src / meta_file
        if meta_path.exists():
            shutil.copy2(meta_path, dst / meta_file)
            copied_files.append(meta_file)
            print(f"  ✅ Copied: {meta_file}")
        else:
            print(f"  ⚠️ Missing: {meta_file}")
    
    print(f"✅ Preview generated at: {dst}")
    print(f"📁 Files copied: {len(copied_files)}")
    
    # Open folder if requested
    if open and os.name == "posix":
        try:
            webbrowser.open(f"file://{dst.resolve()}")
            print(f"🔍 Opened preview folder in browser")
        except Exception as e:
            print(f"⚠️ Could not open folder: {e}")
    
    return True

@task(help={"drop": "Name of the drop bundle"})
def validate(c, drop="eighth_seal_3d"):
    """🔍 Validate preview files for a specific drop."""
    print(f"🔍 Validating preview for drop: {drop}")
    
    src = Path(f"src/xo_core/vault/seals/eighth/drop.assets/{drop}/metadata")
    dst = Path(f"public/vault/previews/{drop}")
    
    validation = {
        "source_exists": src.exists(),
        "destination_exists": dst.exists(),
        "webp_files": [],
        "metadata_files": [],
        "errors": []
    }
    
    if not validation["source_exists"]:
        validation["errors"].append(f"Source path not found: {src}")
        return validation
    
    # Check webp files
    for webp_file in src.glob("*.webp"):
        validation["webp_files"].append(webp_file.name)
    
    # Check metadata files
    for meta_file in ["drop.preview.yml", "drop.status.json"]:
        if (src / meta_file).exists():
            validation["metadata_files"].append(meta_file)
    
    # Validate YAML/JSON if files exist
    for meta_file in validation["metadata_files"]:
        try:
            with open(src / meta_file, 'r') as f:
                if meta_file.endswith('.yml'):
                    yaml.safe_load(f)
                elif meta_file.endswith('.json'):
                    json.load(f)
        except Exception as e:
            validation["errors"].append(f"Invalid {meta_file}: {e}")
    
    # Print results
    print(f"  Source exists: {'✅' if validation['source_exists'] else '❌'}")
    print(f"  Destination exists: {'✅' if validation['destination_exists'] else '❌'}")
    print(f"  WebP files: {len(validation['webp_files'])}")
    print(f"  Metadata files: {len(validation['metadata_files'])}")
    
    if validation["errors"]:
        print(f"  Errors: {len(validation['errors'])}")
        for error in validation["errors"]:
            print(f"    ❌ {error}")
    else:
        print(f"  ✅ Validation passed")
    
    return validation

@task
def list_drops(c):
    """📋 List available drops for preview generation."""
    print("📋 Available drops for preview generation:")
    
    drops_path = Path("src/xo_core/vault/seals/eighth/drop.assets")
    if not drops_path.exists():
        print("  ❌ No drops directory found")
        return
    
    for drop_dir in drops_path.iterdir():
        if drop_dir.is_dir() and not drop_dir.name.startswith('.'):
            metadata_path = drop_dir / "metadata"
            if metadata_path.exists():
                webp_count = len(list(metadata_path.glob("*.webp")))
                meta_files = [f.name for f in metadata_path.iterdir() if f.name in ["drop.preview.yml", "drop.status.json"]]
                status = "✅" if webp_count > 0 else "⚠️"
                print(f"  {status} {drop_dir.name}: {webp_count} webp files, {len(meta_files)} meta files")

@task(help={"drop": "Name of the drop bundle"})
def deploy(c, drop="eighth_seal_3d"):
    """🚀 Deploy preview to public directory and log deployment."""
    print(f"🚀 Deploying preview for drop: {drop}")
    
    # Generate preview
    if not generate(c, drop=drop):
        print(f"❌ Failed to generate preview for {drop}")
        return False
    
    # Log deployment
    log_path = Path("vault/logbook/preview_deploy.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    from datetime import datetime
    with open(log_path, "a") as log_file:
        log_file.write(f"[{datetime.utcnow().isoformat()}] Deployed preview for {drop}\n")
    
    print(f"📝 Logged deployment to {log_path}")
    print(f"✅ Preview deployed successfully for {drop}")
    
    return True

# Create namespace
ns = Collection("preview")
ns.add_task(generate, name="generate")
ns.add_task(validate, name="validate")
ns.add_task(list_drops, name="list")
ns.add_task(deploy, name="deploy")

__all__ = ["ns"]
"""Drop Patch Fabric Tasks - Sync drop metadata and assets from vault to public content."""

import os
import shutil
import json
import yaml
from pathlib import Path
from invoke import task, Collection
from typing import Dict, Any, Optional

# Configuration
VAULT_DROPS_PATH = Path("src/xo_core/vault/seals")
PUBLIC_DROPS_PATH = Path("src/content/drops")
SHARED_META_PATH = Path("src/xo_core/fab_tasks/drop.shared_meta.json")

def load_shared_meta() -> Dict[str, Any]:
    """Load shared metadata for drops."""
    if SHARED_META_PATH.exists():
        with open(SHARED_META_PATH, 'r') as f:
            return json.load(f)
    return {}

def load_drop_yml(drop_id: str) -> Optional[Dict[str, Any]]:
    """Load .drop.yml from vault location."""
    drop_yml_path = VAULT_DROPS_PATH / drop_id / "drop.assets" / ".drop.yml"
    if drop_yml_path.exists():
        with open(drop_yml_path, 'r') as f:
            return yaml.safe_load(f)
    return None

def sync_drop_assets(drop_id: str, force: bool = False) -> bool:
    """Sync drop assets from vault to public content."""
    vault_drop_path = VAULT_DROPS_PATH / drop_id / "drop.assets"
    public_drop_path = PUBLIC_DROPS_PATH / drop_id
    
    if not vault_drop_path.exists():
        print(f"❌ Vault drop path not found: {vault_drop_path}")
        return False
    
    # Create public drop directory if it doesn't exist
    public_drop_path.mkdir(parents=True, exist_ok=True)
    
    # Sync .drop.yml
    drop_yml_src = vault_drop_path / ".drop.yml"
    drop_yml_dst = public_drop_path / ".drop.yml"
    
    if drop_yml_src.exists():
        if not drop_yml_dst.exists() or force:
            shutil.copy2(drop_yml_src, drop_yml_dst)
            print(f"✅ Synced .drop.yml for {drop_id}")
        else:
            print(f"⚠️ .drop.yml already exists for {drop_id} (use --force to overwrite)")
    
    # Sync webp assets
    webp_src = vault_drop_path / "webp"
    webp_dst = public_drop_path / "webp"
    
    if webp_src.exists():
        if webp_dst.exists() and not force:
            print(f"⚠️ webp/ directory already exists for {drop_id} (use --force to overwrite)")
        else:
            if webp_dst.exists():
                shutil.rmtree(webp_dst)
            shutil.copytree(webp_src, webp_dst)
            print(f"✅ Synced webp assets for {drop_id}")
    
    # Sync other assets (png, svg, etc.)
    for asset_ext in ['png', 'svg', 'jpg', 'jpeg']:
        asset_src = vault_drop_path / asset_ext
        asset_dst = public_drop_path / asset_ext
        
        if asset_src.exists():
            if asset_dst.exists() and not force:
                print(f"⚠️ {asset_ext}/ directory already exists for {drop_id}")
            else:
                if asset_dst.exists():
                    shutil.rmtree(asset_dst)
                shutil.copytree(asset_src, asset_dst)
                print(f"✅ Synced {asset_ext} assets for {drop_id}")
    
    return True

def generate_drop_meta(drop_id: str, drop_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate enhanced drop metadata with shared meta."""
    shared_meta = load_shared_meta()
    
    # Base metadata from .drop.yml
    meta = {
        "drop": drop_id,
        "title": drop_data.get("title", f"{drop_id.title()} Drop"),
        "image": drop_data.get("image", "webp/drop-symbol.webp"),
        "variants": drop_data.get("variants", []),
        "created_at": "2025-07-21T00:00:00Z",
        "status": "active"
    }
    
    # Merge with shared metadata
    if drop_id in shared_meta:
        meta.update(shared_meta[drop_id])
    
    return meta

@task(help={
    "drop": "Drop ID to patch (e.g., eighth, first, lolcats)",
    "force": "Force overwrite existing files",
    "list": "List available drops",
    "meta-only": "Only sync metadata, skip assets"
})
def patch_drop_yml(c, drop=None, force=False, list=False, meta_only=False):
    """Patch drop metadata and assets from vault to public content."""
    print("🔧 XO Drop Patch System")
    print("-" * 40)
    
    if list:
        print("📋 Available drops in vault:")
        if VAULT_DROPS_PATH.exists():
            for drop_dir in VAULT_DROPS_PATH.iterdir():
                if drop_dir.is_dir():
                    drop_yml = drop_dir / "drop.assets" / ".drop.yml"
                    status = "✅" if drop_yml.exists() else "❌"
                    print(f"  {status} {drop_dir.name}")
        else:
            print("  No vault drops directory found")
        return
    
    if not drop:
        print("❌ Please specify a drop ID with --drop=<id>")
        print("   Use --list to see available drops")
        return
    
    print(f"🎯 Patching drop: {drop}")
    
    # Load drop data
    drop_data = load_drop_yml(drop)
    if not drop_data:
        print(f"❌ No .drop.yml found for drop: {drop}")
        return
    
    print(f"📄 Drop data loaded: {drop_data.get('title', 'Untitled')}")
    
    # Sync assets (unless meta-only)
    if not meta_only:
        if not sync_drop_assets(drop, force):
            print(f"❌ Failed to sync assets for {drop}")
            return
    
    # Generate and save enhanced metadata
    enhanced_meta = generate_drop_meta(drop, drop_data)
    meta_path = PUBLIC_DROPS_PATH / drop / "drop.meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(meta_path, 'w') as f:
        json.dump(enhanced_meta, f, indent=2)
    
    print(f"✅ Generated enhanced metadata: {meta_path}")
    print(f"🎨 Drop '{drop}' patched successfully!")
    
    # Show summary
    print(f"\n📊 Summary for {drop}:")
    print(f"  Title: {enhanced_meta.get('title')}")
    print(f"  Image: {enhanced_meta.get('image')}")
    print(f"  Variants: {len(enhanced_meta.get('variants', []))}")
    print(f"  Status: {enhanced_meta.get('status')}")

@task
def patch_all(c, force=False):
    """Patch all available drops."""
    print("🔄 Patching all drops...")
    
    if not VAULT_DROPS_PATH.exists():
        print("❌ Vault drops directory not found")
        return
    
    success_count = 0
    total_count = 0
    
    for drop_dir in VAULT_DROPS_PATH.iterdir():
        if drop_dir.is_dir():
            drop_id = drop_dir.name
            drop_yml = drop_dir / "drop.assets" / ".drop.yml"
            
            if drop_yml.exists():
                total_count += 1
                print(f"\n🎯 Processing {drop_id}...")
                
                try:
                    drop_data = load_drop_yml(drop_id)
                    if drop_data and sync_drop_assets(drop_id, force):
                        enhanced_meta = generate_drop_meta(drop_id, drop_data)
                        meta_path = PUBLIC_DROPS_PATH / drop_id / "drop.meta.json"
                        meta_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(meta_path, 'w') as f:
                            json.dump(enhanced_meta, f, indent=2)
                        
                        print(f"✅ {drop_id} patched successfully")
                        success_count += 1
                    else:
                        print(f"❌ Failed to patch {drop_id}")
                except Exception as e:
                    print(f"❌ Error patching {drop_id}: {e}")
    
    print(f"\n🎉 Patch complete: {success_count}/{total_count} drops processed")

@task
def validate_drops(c):
    """Validate all drops have required assets and metadata."""
    print("🔍 Validating drops...")
    
    if not VAULT_DROPS_PATH.exists():
        print("❌ Vault drops directory not found")
        return
    
    all_valid = True
    
    for drop_dir in VAULT_DROPS_PATH.iterdir():
        if drop_dir.is_dir():
            drop_id = drop_dir.name
            drop_assets = drop_dir / "drop.assets"
            
            print(f"\n🔍 {drop_id}:")
            
            # Check .drop.yml
            drop_yml = drop_assets / ".drop.yml"
            if drop_yml.exists():
                print(f"  ✅ .drop.yml")
            else:
                print(f"  ❌ Missing .drop.yml")
                all_valid = False
            
            # Check webp assets
            webp_dir = drop_assets / "webp"
            if webp_dir.exists():
                webp_files = list(webp_dir.glob("*.webp"))
                print(f"  ✅ webp/ ({len(webp_files)} files)")
            else:
                print(f"  ⚠️ No webp/ directory")
            
            # Check public sync
            public_drop = PUBLIC_DROPS_PATH / drop_id
            if public_drop.exists():
                print(f"  ✅ Public content synced")
            else:
                print(f"  ⚠️ Not synced to public content")
    
    if all_valid:
        print(f"\n🎉 All drops validated successfully!")
    else:
        print(f"\n⚠️ Some drops have issues")

# Create namespace
ns = Collection("drop_patch")
ns.add_task(patch_drop_yml, name="patch")
ns.add_task(patch_all, name="patch-all")
ns.add_task(validate_drops, name="validate")

__all__ = ["ns"]
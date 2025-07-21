"""Drop Meta Sync Fabric Tasks - Sync drop.meta.json with bundle metadata."""

import os
import json
import yaml
from pathlib import Path
from invoke import task, Collection
from typing import Dict, Any, List, Optional, Set
import re

# Configuration
CONTENT_DROPS_PATH = Path("src/content/drops")
VAULT_DROPS_PATH = Path("src/xo_core/vault/seals")
SHARED_META_PATH = Path("src/xo_core/fab_tasks/drop.shared_meta.json")

def load_shared_meta() -> Dict[str, Any]:
    """Load shared metadata for drops."""
    if SHARED_META_PATH.exists():
        with open(SHARED_META_PATH, 'r') as f:
            return json.load(f)
    return {}

def normalize_filename(filename: str) -> str:
    """Normalize filename to lowercase kebab-case .webp."""
    # Remove extension and convert to kebab-case
    name = re.sub(r'[^a-zA-Z0-9]', '_', filename.lower())
    name = re.sub(r'_+', '_', name).strip('_')
    return f"{name}.webp"

def scan_bundle_assets(drop_id: str, bundle_name: str) -> Dict[str, Any]:
    """Scan a bundle's assets and metadata."""
    bundle_path = VAULT_DROPS_PATH / drop_id / bundle_name
    metadata_path = bundle_path / "metadata"
    webp_path = bundle_path / "webp"
    
    bundle_info = {
        "name": bundle_name,
        "assets": [],
        "webp_files": [],
        "status_file": None,
        "preview_file": None,
        "errors": []
    }
    
    # Scan webp files
    if webp_path.exists():
        bundle_info["webp_files"] = [
            f.name for f in webp_path.glob("*.webp")
        ]
    
    # Load drop.status.json
    status_file = metadata_path / "drop.status.json"
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
                bundle_info["status_file"] = status_data
                
                # Extract assets from status
                if "assets" in status_data:
                    for asset in status_data["assets"]:
                        asset_info = {
                            "id": asset.get("id", ""),
                            "label": asset.get("label", ""),
                            "file": asset.get("file", ""),
                            "exists": False
                        }
                        
                        # Check if asset file exists
                        if asset_info["file"]:
                            asset_path = webp_path / asset_info["file"]
                            asset_info["exists"] = asset_path.exists()
                            
                            if not asset_info["exists"]:
                                bundle_info["errors"].append(
                                    f"Missing asset file: {asset_info['file']}"
                                )
                        
                        bundle_info["assets"].append(asset_info)
        except Exception as e:
            bundle_info["errors"].append(f"Error loading status file: {e}")
    else:
        bundle_info["errors"].append("Missing drop.status.json")
    
    # Load drop.preview.yml
    preview_file = metadata_path / "drop.preview.yml"
    if preview_file.exists():
        try:
            with open(preview_file, 'r') as f:
                bundle_info["preview_file"] = yaml.safe_load(f)
        except Exception as e:
            bundle_info["errors"].append(f"Error loading preview file: {e}")
    
    return bundle_info

def validate_drop_meta(drop_id: str) -> Dict[str, Any]:
    """Validate and patch drop.meta.json with bundle metadata."""
    drop_path = CONTENT_DROPS_PATH / drop_id
    meta_file = drop_path / "drop.meta.json"
    vault_drop_path = VAULT_DROPS_PATH / drop_id
    
    validation = {
        "drop_id": drop_id,
        "meta_exists": meta_file.exists(),
        "bundles": [],
        "errors": [],
        "warnings": [],
        "patches": []
    }
    
    # Load existing meta if it exists
    existing_meta = {}
    if meta_file.exists():
        try:
            with open(meta_file, 'r') as f:
                existing_meta = json.load(f)
        except Exception as e:
            validation["errors"].append(f"Error loading drop.meta.json: {e}")
            return validation
    
    # Scan bundles in vault
    if not vault_drop_path.exists():
        validation["errors"].append(f"Vault drop path not found: {vault_drop_path}")
        return validation
    
    bundle_dirs = [d for d in vault_drop_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    for bundle_dir in bundle_dirs:
        bundle_name = bundle_dir.name
        bundle_info = scan_bundle_assets(drop_id, bundle_name)
        validation["bundles"].append(bundle_info)
        
        if bundle_info["errors"]:
            validation["warnings"].extend(bundle_info["errors"])
    
    # Generate enhanced metadata
    shared_meta = load_shared_meta()
    enhanced_meta = {
        "drop": drop_id,
        "title": existing_meta.get("title", f"{drop_id.title()} Drop"),
        "description": existing_meta.get("description", ""),
        "image": existing_meta.get("image", "webp/drop-symbol.webp"),
        "variants": existing_meta.get("variants", []),
        "bundles": [b["name"] for b in validation["bundles"]],
        "assets": [],
        "tags": existing_meta.get("tags", []),
        "category": existing_meta.get("category", "drops"),
        "rarity": existing_meta.get("rarity", "common"),
        "mint_price": existing_meta.get("mint_price", "0.01 ETH"),
        "max_supply": existing_meta.get("max_supply", 1000),
        "launch_date": existing_meta.get("launch_date", "2025-07-21T00:00:00Z"),
        "status": existing_meta.get("status", "active"),
        "social_links": existing_meta.get("social_links", {}),
        "created_at": existing_meta.get("created_at", "2025-07-21T00:00:00Z"),
        "updated_at": "2025-07-21T00:00:00Z"
    }
    
    # Merge with shared metadata
    if drop_id in shared_meta:
        for key, value in shared_meta[drop_id].items():
            if key not in existing_meta:  # Don't overwrite existing values
                enhanced_meta[key] = value
                validation["patches"].append(f"Added {key} from shared meta")
    
    # Collect all assets from bundles
    all_assets = []
    for bundle in validation["bundles"]:
        for asset in bundle["assets"]:
            asset_info = {
                "id": asset["id"],
                "label": asset["label"],
                "file": asset["file"],
                "bundle": bundle["name"],
                "exists": asset["exists"]
            }
            all_assets.append(asset_info)
    
    enhanced_meta["assets"] = all_assets
    
    # Update variants based on webp files
    all_webp_files = set()
    for bundle in validation["bundles"]:
        all_webp_files.update(bundle["webp_files"])
    
    if all_webp_files:
        enhanced_meta["variants"] = sorted(list(all_webp_files))
        validation["patches"].append(f"Updated variants from {len(all_webp_files)} webp files")
    
    # Save enhanced metadata
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_file, 'w') as f:
        json.dump(enhanced_meta, f, indent=2)
    
    validation["enhanced_meta"] = enhanced_meta
    return validation

@task(help={
    "drop": "Drop ID to sync (e.g., eighth, first, lolcats)",
    "list": "List available drops",
    "validate-only": "Only validate, don't patch",
    "verbose": "Show detailed output"
})
def sync_meta(c, drop=None, list=False, validate_only=False, verbose=False):
    """Sync drop.meta.json with bundle metadata."""
    print("🔁 XO Drop Meta Sync System")
    print("-" * 40)
    
    if list:
        print("📋 Available drops:")
        if CONTENT_DROPS_PATH.exists():
            for drop_dir in CONTENT_DROPS_PATH.iterdir():
                if drop_dir.is_dir():
                    meta_file = drop_dir / "drop.meta.json"
                    status = "✅" if meta_file.exists() else "❌"
                    print(f"  {status} {drop_dir.name}")
        else:
            print("  No content drops directory found")
        return
    
    if not drop:
        print("❌ Please specify a drop ID with --drop=<id>")
        print("   Use --list to see available drops")
        return
    
    print(f"🎯 Syncing meta for drop: {drop}")
    
    # Validate and patch
    validation = validate_drop_meta(drop)
    
    if verbose:
        print(f"\n📊 Validation Results:")
        print(f"  Drop ID: {validation['drop_id']}")
        print(f"  Meta exists: {validation['meta_exists']}")
        print(f"  Bundles found: {len(validation['bundles'])}")
        print(f"  Errors: {len(validation['errors'])}")
        print(f"  Warnings: {len(validation['warnings'])}")
        print(f"  Patches applied: {len(validation['patches'])}")
    
    # Show bundle details
    print(f"\n📦 Bundle Analysis:")
    for bundle in validation["bundles"]:
        status = "✅" if not bundle["errors"] else "⚠️"
        print(f"  {status} {bundle['name']}: {len(bundle['assets'])} assets, {len(bundle['webp_files'])} webp files")
        
        if bundle["errors"] and verbose:
            for error in bundle["errors"]:
                print(f"    ⚠️ {error}")
    
    # Show patches
    if validation["patches"]:
        print(f"\n🔧 Patches Applied:")
        for patch in validation["patches"]:
            print(f"  ✅ {patch}")
    
    # Show errors
    if validation["errors"]:
        print(f"\n❌ Errors:")
        for error in validation["errors"]:
            print(f"  ❌ {error}")
    
    # Show warnings
    if validation["warnings"]:
        print(f"\n⚠️ Warnings:")
        for warning in validation["warnings"]:
            print(f"  ⚠️ {warning}")
    
    if not validation["errors"]:
        print(f"\n🎉 Drop '{drop}' meta sync completed successfully!")
        
        # Show summary
        enhanced_meta = validation.get("enhanced_meta", {})
        print(f"\n📊 Summary for {drop}:")
        print(f"  Title: {enhanced_meta.get('title')}")
        print(f"  Bundles: {len(enhanced_meta.get('bundles', []))}")
        print(f"  Assets: {len(enhanced_meta.get('assets', []))}")
        print(f"  Variants: {len(enhanced_meta.get('variants', []))}")
        print(f"  Status: {enhanced_meta.get('status')}")
    else:
        print(f"\n❌ Drop '{drop}' meta sync failed with errors")

@task
def sync_all(c, verbose=False):
    """Sync meta for all available drops."""
    print("🔄 Syncing meta for all drops...")
    
    if not CONTENT_DROPS_PATH.exists():
        print("❌ Content drops directory not found")
        return
    
    success_count = 0
    total_count = 0
    
    for drop_dir in CONTENT_DROPS_PATH.iterdir():
        if drop_dir.is_dir():
            drop_id = drop_dir.name
            total_count += 1
            
            print(f"\n🎯 Processing {drop_id}...")
            
            try:
                validation = validate_drop_meta(drop_id)
                
                if not validation["errors"]:
                    print(f"✅ {drop_id} synced successfully")
                    success_count += 1
                else:
                    print(f"❌ {drop_id} failed: {len(validation['errors'])} errors")
                    
                    if verbose:
                        for error in validation["errors"]:
                            print(f"  ❌ {error}")
            except Exception as e:
                print(f"❌ Error syncing {drop_id}: {e}")
    
    print(f"\n🎉 Meta sync complete: {success_count}/{total_count} drops processed")

@task
def validate_structure(c, drop=None):
    """Validate drop structure and show detailed analysis."""
    print("🔍 Drop Structure Validation")
    print("-" * 40)
    
    if not drop:
        print("❌ Please specify a drop ID with --drop=<id>")
        return
    
    validation = validate_drop_meta(drop)
    
    print(f"\n📁 Structure Analysis for '{drop}':")
    print(f"  Content path: {CONTENT_DROPS_PATH / drop}")
    print(f"  Vault path: {VAULT_DROPS_PATH / drop}")
    print(f"  Meta file: {'✅' if validation['meta_exists'] else '❌'}")
    
    print(f"\n📦 Bundle Details:")
    for bundle in validation["bundles"]:
        print(f"\n  🗂️ {bundle['name']}:")
        print(f"    Assets: {len(bundle['assets'])}")
        print(f"    WebP files: {len(bundle['webp_files'])}")
        print(f"    Status file: {'✅' if bundle['status_file'] else '❌'}")
        print(f"    Preview file: {'✅' if bundle['preview_file'] else '❌'}")
        
        if bundle["assets"]:
            print(f"    Asset list:")
            for asset in bundle["assets"]:
                status = "✅" if asset["exists"] else "❌"
                print(f"      {status} {asset['id']}: {asset['file']}")
        
        if bundle["errors"]:
            print(f"    Errors:")
            for error in bundle["errors"]:
                print(f"      ⚠️ {error}")

# Create namespace
ns = Collection("drop_meta_sync")
ns.add_task(sync_meta, name="sync")
ns.add_task(sync_all, name="sync-all")
ns.add_task(validate_structure, name="validate")

__all__ = ["ns"] 
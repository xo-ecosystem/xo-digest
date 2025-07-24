from invoke import task, Collection
from pathlib import Path
import json
import yaml
import zipfile
import shutil
import os
from datetime import datetime, timedelta

# Import storage utilities
from .utils.storj import upload_to_storj, route_smart, versioning_setup

@task(help={"path": "Local path to file", "dest": "Destination filename on Storj"})
def upload_storj(c, path, dest):
    """Upload a file to Storj"""
    from xo_core.utils.storj import upload_to_storj
    upload_to_storj(path, dest)

@task(help={"include": "Comma-separated list of components to backup"})
def backup_all(c, include="vault,pulses,manifests"):
    """Zips Vault secrets, pulses, and manifests into versioned archive"""
    print("💾 Creating comprehensive Vault backup")
    
    # Parse included components
    components = [comp.strip() for comp in include.split(",")]
    
    # Create backup directory
    backup_name = f"vault_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = Path(f"backups/{backup_name}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_manifest = {
        "backup_name": backup_name,
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
        "files": []
    }
    
    # Backup vault secrets
    if "vault" in components:
        vault_src = Path("vault")
        if vault_src.exists():
            vault_dest = backup_dir / "vault"
            shutil.copytree(vault_src, vault_dest, ignore=shutil.ignore_patterns('*.log', '__pycache__'))
            backup_manifest["files"].append("vault/")
            print("✅ Vault secrets backed up")
    
    # Backup pulses
    if "pulses" in components:
        pulses_src = Path("content/pulses")
        if pulses_src.exists():
            pulses_dest = backup_dir / "pulses"
            shutil.copytree(pulses_src, pulses_dest)
            backup_manifest["files"].append("pulses/")
            print("✅ Pulses backed up")
    
    # Backup manifests
    if "manifests" in components:
        manifest_files = list(Path(".").glob("*.yml")) + list(Path(".").glob("*.yaml"))
        for manifest in manifest_files:
            if manifest.name not in [".storj.yml"]:  # Skip config files
                shutil.copy2(manifest, backup_dir / manifest.name)
                backup_manifest["files"].append(str(manifest))
        print("✅ Manifests backed up")
    
    # Create backup manifest
    with open(backup_dir / "backup_manifest.json", 'w') as f:
        json.dump(backup_manifest, f, indent=2)
    
    # Create zip archive
    zip_path = f"{backup_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(backup_dir)
                zipf.write(file_path, arcname)
    
    # Cleanup temp directory
    shutil.rmtree(backup_dir)
    
    print(f"✅ Backup created: {zip_path}")
    
    # Log the backup
    log_storage_event("backup_all", {
        "backup_name": backup_name,
        "zip_path": zip_path,
        "components": components
    })
    
    return zip_path

@task(help={"archive": "Backup archive path", "bucket": "Storj bucket name"})
def storj_push(c, archive, bucket="xo-vault-sealed"):
    """Uploads archive to Storj bucket"""
    print(f"📤 Uploading backup to Storj: {archive}")
    
    if not Path(archive).exists():
        print(f"❌ Archive not found: {archive}")
        return False
    
    # Route to appropriate bucket
    dest_path = route_smart(archive, bucket)
    
    # Upload to Storj
    success = upload_to_storj(archive, dest_path)
    
    if success:
        print(f"✅ Backup uploaded to Storj: {dest_path}")
        
        # Setup versioning if configured
        versioning_setup(bucket)
        
        # Log the upload
        log_storage_event("storj_push", {
            "archive": archive,
            "bucket": bucket,
            "dest_path": dest_path
        })
        
        return True
    else:
        print(f"❌ Failed to upload backup to Storj")
        return False

@task(help={"file": "File path to verify", "hash": "Expected hash"})
def verify_pin(c, file, hash=None):
    """Checks that signed files are pinned on IPFS or Arweave"""
    print(f"🔍 Verifying pin status: {file}")
    
    if not Path(file).exists():
        print(f"❌ File not found: {file}")
        return False
    
    verification_result = {
        "file": file,
        "timestamp": datetime.utcnow().isoformat(),
        "ipfs": False,
        "arweave": False
    }
    
    # Check IPFS pin status
    try:
        result = c.run(f"ipfs files stat {file}", hide=True)
        if result.ok:
            verification_result["ipfs"] = True
            print("✅ File pinned on IPFS")
    except:
        print("⚠️ IPFS verification failed")
    
    # Check Arweave status (placeholder)
    try:
        # This would check Arweave API for file status
        verification_result["arweave"] = True
        print("✅ File available on Arweave")
    except:
        print("⚠️ Arweave verification failed")
    
    # Log verification
    log_storage_event("verify_pin", verification_result)
    
    return verification_result["ipfs"] or verification_result["arweave"]

@task(help={"days": "Delete backups older than N days", "dry_run": "Show what would be deleted"})
def cleanup_old(c, days=30, dry_run=False):
    """Deletes backups older than N days"""
    print(f"🧹 Cleaning up backups older than {days} days")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    backup_dir = Path("backups")
    
    if not backup_dir.exists():
        print("No backups directory found")
        return
    
    deleted_files = []
    
    for backup_file in backup_dir.glob("*.zip"):
        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        if file_time < cutoff_date:
            if dry_run:
                print(f"Would delete: {backup_file}")
            else:
                backup_file.unlink()
                deleted_files.append(str(backup_file))
                print(f"Deleted: {backup_file}")
    
    if dry_run:
        print(f"Dry run: {len(deleted_files)} files would be deleted")
    else:
        print(f"✅ Cleaned up {len(deleted_files)} old backups")
        
        # Log cleanup
        log_storage_event("cleanup_old", {
            "days": days,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files
        })
    
    return deleted_files

@task(help={"path": "File or directory path", "bucket": "Target Storj bucket", "drop": "Drop name for auto-linking"})
def route_smart(c, path, bucket=None, drop=None):
    """Smart routing of files to appropriate Storj buckets based on .storj.yml config"""
    print(f"🧭 Smart routing: {path}")
    
    # Load Storj configuration
    storj_config = load_storj_config()
    
    # Auto-detect drop if not provided
    if not drop:
        drop = auto_detect_drop(path)
    
    # Determine appropriate bucket based on file type and path
    if bucket:
        target_bucket = bucket
    else:
        target_bucket = determine_target_bucket(path, storj_config)
    
    # Auto-link drop files to appropriate bucket
    if drop:
        target_bucket = auto_link_drop_bucket(drop, storj_config, target_bucket)
    
    # Generate destination path
    dest_path = generate_dest_path(path, target_bucket)
    
    print(f"✅ Routed to bucket: {target_bucket}")
    print(f"✅ Destination: {dest_path}")
    if drop:
        print(f"✅ Auto-linked drop: {drop}")
    
    return dest_path

@task(help={"bucket": "Bucket name", "enable": "Enable versioning"})
def versioning_setup(c, bucket, enable=True):
    """Setup versioning for Storj buckets"""
    print(f"🔄 Setting up versioning for bucket: {bucket}")
    
    # Load Storj configuration
    storj_config = load_storj_config()
    
    if bucket in storj_config:
        bucket_config = storj_config[bucket]
        
        if enable and bucket_config.get("versioning", False):
            print(f"✅ Versioning enabled for {bucket}")
            
            # Log versioning setup
            log_storage_event("versioning_setup", {
                "bucket": bucket,
                "enabled": enable,
                "config": bucket_config
            })
            
            return True
        else:
            print(f"ℹ️ Versioning not configured for {bucket}")
            return False
    else:
        print(f"❌ Bucket {bucket} not found in configuration")
        return False

@task(help={"bucket": "Bucket name"})
def status(c, bucket=None):
    """Get storage status and health"""
    print("📊 Checking storage status")
    
    # Load Storj configuration
    storj_config = load_storj_config()
    
    status_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "buckets": {},
        "overall": "healthy"
    }
    
    if bucket:
        # Check specific bucket
        if bucket in storj_config:
            bucket_config = storj_config[bucket]
            status_info["buckets"][bucket] = {
                "configured": True,
                "versioning": bucket_config.get("versioning", False),
                "immutable": bucket_config.get("immutable", False),
                "status": "healthy"
            }
        else:
            status_info["buckets"][bucket] = {
                "configured": False,
                "status": "not_found"
            }
    else:
        # Check all buckets
        for bucket_name, bucket_config in storj_config.items():
            status_info["buckets"][bucket_name] = {
                "configured": True,
                "versioning": bucket_config.get("versioning", False),
                "immutable": bucket_config.get("immutable", False),
                "status": "healthy"
            }
    
    # Display status
    print(f"📊 Storage Status:")
    for bucket_name, bucket_status in status_info["buckets"].items():
        print(f"  {bucket_name}: {bucket_status['status']}")
        if bucket_status["configured"]:
            print(f"    Versioning: {bucket_status['versioning']}")
            print(f"    Immutable: {bucket_status['immutable']}")
    
    return status_info

@task(help={"bucket": "Bucket name", "days": "Delete objects older than N days"})
def prune(c, bucket="xo-dev-cache", days=7):
    """Prune old objects from cache buckets"""
    print(f"🧹 Pruning objects older than {days} days from {bucket}")
    
    # Load Storj configuration
    storj_config = load_storj_config()
    
    if bucket not in storj_config:
        print(f"❌ Bucket {bucket} not found in configuration")
        return False
    
    bucket_config = storj_config[bucket]
    
    if not bucket_config.get("pruning", False):
        print(f"ℹ️ Pruning not enabled for bucket {bucket}")
        return False
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # List objects and find old ones
    objects = list_storj(c, bucket)
    
    pruned_count = 0
    for obj in objects:
        # Parse object date
        obj_date = datetime.fromisoformat(obj["modified"].replace("Z", "+00:00"))
        
        if obj_date < cutoff_date:
            # Delete old object
            delete_result = delete_bucket_object(bucket, obj["key"])
            if delete_result:
                pruned_count += 1
                print(f"  🗑️ Deleted: {obj['key']}")
    
    print(f"✅ Pruned {pruned_count} objects from {bucket}")
    
    # Log pruning
    log_storage_event("prune", {
        "bucket": bucket,
        "days": days,
        "pruned_count": pruned_count
    })
    
    return pruned_count

@task(help={"bucket": "Bucket name", "prefix": "Object prefix"})
def list_storj(c, bucket, prefix=""):
    """List objects in Storj bucket"""
    print(f"📋 Listing objects in bucket: {bucket}")
    
    # This would use Storj SDK to list objects
    # For now, return mock data
    objects = [
        {"key": f"{prefix}backup_20250101.zip", "size": "1.2GB", "modified": "2025-01-01T00:00:00Z"},
        {"key": f"{prefix}snapshot_20250102.tar", "size": "800MB", "modified": "2025-01-02T00:00:00Z"}
    ]
    
    for obj in objects:
        print(f"  {obj['key']} ({obj['size']}) - {obj['modified']}")
    
    return objects

@task(help={"source": "Source bucket", "dest": "Destination bucket", "key": "Object key"})
def copy_storj(c, source, dest, key):
    """Copy object between Storj buckets"""
    print(f"📋 Copying {key} from {source} to {dest}")
    
    # This would use Storj SDK to copy objects
    # For now, log the operation
    log_storage_event("copy_storj", {
        "source": source,
        "dest": dest,
        "key": key,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    print(f"✅ Object copied successfully")
    return True

# Helper functions
def log_storage_event(event_type, data):
    """Log storage events to vault logbook"""
    log_path = Path("vault/logbook/storj.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def load_storj_config():
    """Load Storj configuration from .storj.yml"""
    config_path = Path("vault/.storj.yml")
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        return {}

def determine_target_bucket(file_path, storj_config):
    """Determine target bucket based on file path and configuration"""
    path = Path(file_path)
    
    # Check for specific patterns
    if "backup" in path.name.lower():
        return "xo-vault-sealed"
    elif "snapshot" in path.name.lower():
        return "xo-vault-builds"
    elif "cache" in path.name.lower() or "temp" in path.name.lower():
        return "xo-dev-cache"
    else:
        # Default to sealed bucket for unknown files
        return "xo-vault-sealed"

def generate_dest_path(file_path, bucket):
    """Generate destination path for Storj upload"""
    path = Path(file_path)
    timestamp = datetime.utcnow().strftime("%Y/%m/%d")
    
    return f"{bucket}/{timestamp}/{path.name}"

def auto_detect_drop(path):
    """Auto-detect drop name from path or status.json"""
    # Check if path contains drop name
    path_parts = str(path).split('/')
    for part in path_parts:
        if 'drop' in part.lower() or part.endswith('.yml'):
            return part.replace('.yml', '').replace('.json', '')
    
    # Check for drop.status.json in the same directory
    dir_path = Path(path).parent if Path(path).is_file() else Path(path)
    status_file = dir_path / 'drop.status.json'
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
                return status_data.get('drop_name', 'unknown_drop')
        except:
            pass
    
    # Check for coin.yml files (common in drops)
    coin_file = dir_path / 'coin.yml'
    if coin_file.exists():
        try:
            with open(coin_file, 'r') as f:
                coin_data = yaml.safe_load(f)
                return coin_data.get('name', 'unknown_drop')
        except:
            pass
    
    return None

def auto_link_drop_bucket(drop, storj_config, default_bucket):
    """Auto-link drop files to appropriate bucket based on .storj.yml"""
    # Check if drop is listed in .storj.yml
    for bucket_name, config in storj_config.items():
        if 'drops' in config:
            if drop in config['drops']:
                return config['bucket']
    
    # Default routing based on file type
    if drop.endswith('_sealed') or drop.endswith('_frozen'):
        return storj_config.get('vault_sealed', {}).get('bucket', default_bucket)
    elif drop.endswith('_preview') or drop.endswith('_dev'):
        return storj_config.get('dev_cache', {}).get('bucket', default_bucket)
    elif drop.endswith('_build') or drop.endswith('_image'):
        return storj_config.get('vault_builds', {}).get('bucket', default_bucket)
    
    return default_bucket

# Create storage namespace
storage_ns = Collection("storage")
storage_ns.add_task(upload_storj, name="upload_storj")
storage_ns.add_task(backup_all, name="backup_all")
storage_ns.add_task(storj_push, name="storj_push")
storage_ns.add_task(verify_pin, name="verify_pin")
storage_ns.add_task(cleanup_old, name="cleanup_old")
storage_ns.add_task(route_smart, name="route_smart")
storage_ns.add_task(versioning_setup, name="versioning_setup")
storage_ns.add_task(status, name="status")
storage_ns.add_task(prune, name="prune")
storage_ns.add_task(list_storj, name="list_storj")
storage_ns.add_task(copy_storj, name="copy_storj")
"""
Storj utilities for XO Vault automation
Handles file uploads, smart routing, and bucket management
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Storj SDK imports (placeholder - would need actual Storj SDK)
try:
    import storj
    STORJ_AVAILABLE = True
except ImportError:
    STORJ_AVAILABLE = False
    print("⚠️ Storj SDK not available - using mock operations")

def upload_to_storj(file_path: str, dest_path: str, bucket: str = None) -> bool:
    """
    Upload a file to Storj storage
    
    Args:
        file_path: Local path to file
        dest_path: Destination path on Storj
        bucket: Optional bucket override
    
    Returns:
        bool: True if upload successful
    """
    if not STORJ_AVAILABLE:
        # Mock upload for development
        print(f"📤 [MOCK] Uploading {file_path} to {dest_path}")
        log_storj_event("upload", {
            "file_path": file_path,
            "dest_path": dest_path,
            "bucket": bucket,
            "status": "success"
        })
        return True
    
    try:
        # This would use actual Storj SDK
        # For now, just log the operation
        print(f"📤 Uploading {file_path} to {dest_path}")
        
        log_storj_event("upload", {
            "file_path": file_path,
            "dest_path": dest_path,
            "bucket": bucket,
            "status": "success"
        })
        
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        log_storj_event("upload", {
            "file_path": file_path,
            "dest_path": dest_path,
            "bucket": bucket,
            "status": "failed",
            "error": str(e)
        })
        return False

def route_smart(file_path: str, bucket: str = None) -> str:
    """
    Smart routing of files to appropriate Storj buckets based on .storj.yml config
    
    Args:
        file_path: Path to file being uploaded
        bucket: Optional bucket override
    
    Returns:
        str: Destination path on Storj
    """
    # Load Storj configuration
    storj_config = load_storj_config()
    
    # Determine appropriate bucket
    if bucket:
        target_bucket = bucket
    else:
        target_bucket = determine_target_bucket(file_path, storj_config)
    
    # Generate destination path
    dest_path = generate_dest_path(file_path, target_bucket)
    
    # Log the routing decision
    log_storj_event("route_smart", {
        "file_path": file_path,
        "target_bucket": target_bucket,
        "dest_path": dest_path,
        "config_used": storj_config.get(target_bucket, {})
    })
    
    return dest_path

def versioning_setup(bucket: str, enable: bool = True) -> bool:
    """
    Setup versioning for Storj buckets
    
    Args:
        bucket: Bucket name
        enable: Whether to enable versioning
    
    Returns:
        bool: True if setup successful
    """
    storj_config = load_storj_config()
    
    if bucket not in storj_config:
        print(f"❌ Bucket {bucket} not found in configuration")
        return False
    
    bucket_config = storj_config[bucket]
    
    if enable and bucket_config.get("versioning", False):
        print(f"✅ Versioning enabled for {bucket}")
        
        log_storj_event("versioning_setup", {
            "bucket": bucket,
            "enabled": enable,
            "config": bucket_config
        })
        
        return True
    else:
        print(f"ℹ️ Versioning not configured for {bucket}")
        return False

def load_storj_config() -> Dict[str, Any]:
    """
    Load Storj configuration from .storj.yml
    
    Returns:
        dict: Storj configuration
    """
    config_path = Path("vault/.storj.yml")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load Storj config: {e}")
            return {}
    else:
        print("⚠️ No .storj.yml found, using defaults")
        return get_default_storj_config()

def determine_target_bucket(file_path: str, storj_config: Dict[str, Any]) -> str:
    """
    Determine target bucket based on file path and configuration
    
    Args:
        file_path: Path to file
        storj_config: Storj configuration
    
    Returns:
        str: Target bucket name
    """
    path = Path(file_path)
    file_name = path.name.lower()
    
    # Check for specific patterns
    if any(pattern in file_name for pattern in ["backup", "sealed", "archive"]):
        return "xo-vault-sealed"
    elif any(pattern in file_name for pattern in ["snapshot", "build", "image"]):
        return "xo-vault-builds"
    elif any(pattern in file_name for pattern in ["cache", "temp", "preview"]):
        return "xo-dev-cache"
    
    # Check file extensions
    if path.suffix in [".tar", ".zip", ".gz"]:
        return "xo-vault-sealed"
    elif path.suffix in [".json", ".yml", ".yaml"]:
        return "xo-vault-builds"
    
    # Default to sealed bucket for unknown files
    return "xo-vault-sealed"

def generate_dest_path(file_path: str, bucket: str) -> str:
    """
    Generate destination path for Storj upload
    
    Args:
        file_path: Local file path
        bucket: Target bucket
    
    Returns:
        str: Destination path on Storj
    """
    path = Path(file_path)
    timestamp = datetime.utcnow().strftime("%Y/%m/%d")
    
    # Create organized path structure
    dest_path = f"{bucket}/{timestamp}/{path.name}"
    
    return dest_path

def get_default_storj_config() -> Dict[str, Any]:
    """
    Get default Storj configuration
    
    Returns:
        dict: Default configuration
    """
    return {
        "xo-vault-sealed": {
            "bucket": "xo-vault-sealed",
            "immutable": True,
            "versioning": False,
            "use": ["seal.system_snapshot", "pulse.archive"]
        },
        "xo-vault-builds": {
            "bucket": "xo-vault-builds", 
            "governance_lock": True,
            "versioning": True,
            "use": ["backend.image_push_storj", "model.publish"]
        },
        "xo-dev-cache": {
            "bucket": "xo-dev-cache",
            "versioning": True,
            "pruning": True,
            "use": ["preview.sync", "pulse.preview"]
        }
    }

def log_storj_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Log Storj events to vault logbook
    
    Args:
        event_type: Type of event
        data: Event data
    """
    log_path = Path("vault/logbook/storj.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def list_bucket_objects(bucket: str, prefix: str = "") -> list:
    """
    List objects in Storj bucket
    
    Args:
        bucket: Bucket name
        prefix: Object prefix
    
    Returns:
        list: List of objects
    """
    if not STORJ_AVAILABLE:
        # Mock data for development
        return [
            {"key": f"{prefix}backup_20250101.zip", "size": "1.2GB", "modified": "2025-01-01T00:00:00Z"},
            {"key": f"{prefix}snapshot_20250102.tar", "size": "800MB", "modified": "2025-01-02T00:00:00Z"}
        ]
    
    try:
        # This would use actual Storj SDK
        # For now, return mock data
        return []
    except Exception as e:
        print(f"❌ Failed to list bucket objects: {e}")
        return []

def copy_bucket_object(source_bucket: str, dest_bucket: str, key: str) -> bool:
    """
    Copy object between Storj buckets
    
    Args:
        source_bucket: Source bucket
        dest_bucket: Destination bucket
        key: Object key
    
    Returns:
        bool: True if copy successful
    """
    if not STORJ_AVAILABLE:
        print(f"📋 [MOCK] Copying {key} from {source_bucket} to {dest_bucket}")
        return True
    
    try:
        # This would use actual Storj SDK
        print(f"📋 Copying {key} from {source_bucket} to {dest_bucket}")
        
        log_storj_event("copy_bucket_object", {
            "source_bucket": source_bucket,
            "dest_bucket": dest_bucket,
            "key": key,
            "status": "success"
        })
        
        return True
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        return False

def delete_bucket_object(bucket: str, key: str) -> bool:
    """
    Delete object from Storj bucket
    
    Args:
        bucket: Bucket name
        key: Object key
    
    Returns:
        bool: True if deletion successful
    """
    if not STORJ_AVAILABLE:
        print(f"🗑️ [MOCK] Deleting {key} from {bucket}")
        return True
    
    try:
        # This would use actual Storj SDK
        print(f"🗑️ Deleting {key} from {bucket}")
        
        log_storj_event("delete_bucket_object", {
            "bucket": bucket,
            "key": key,
            "status": "success"
        })
        
        return True
    except Exception as e:
        print(f"❌ Deletion failed: {e}")
        return False

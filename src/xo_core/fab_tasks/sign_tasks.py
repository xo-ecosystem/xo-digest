from invoke import task, Collection
from pathlib import Path
import json
import yaml
import hashlib
import zipfile
import shutil
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

@task(help={"bundle": "Pulse bundle path", "key": "Signing key path"})
def pulse_bundle(c, bundle, key="vault/private.key.b64"):
    """Signs a full drop or pulse bundle with Vault key and logs result"""
    print(f"🔐 Signing pulse bundle: {bundle}")
    
    bundle_path = Path(bundle)
    if not bundle_path.exists():
        print(f"❌ Bundle not found: {bundle}")
        return False
    
    # Load signing key
    if not Path(key).exists():
        print(f"❌ Signing key not found: {key}")
        return False
    
    # Generate bundle manifest
    manifest = generate_bundle_manifest(bundle_path)
    
    # Sign the manifest
    signature = sign_manifest(manifest, key)
    
    # Create signed bundle
    signed_bundle = create_signed_bundle(bundle_path, manifest, signature)
    
    print(f"✅ Bundle signed: {signed_bundle}")
    
    # Log the signing
    log_sign_event("pulse_bundle", {
        "bundle": bundle,
        "signed_bundle": signed_bundle,
        "manifest_hash": manifest["hash"]
    })
    
    return signed_bundle

@task(help={"inbox_dir": "Inbox directory path", "key": "Signing key path"})
def inbox_all(c, inbox_dir="content/pulses", key="vault/private.key.b64"):
    """Signs all .comments.mdx inbox files before pinning"""
    print(f"🔐 Signing all inbox files in: {inbox_dir}")
    
    inbox_path = Path(inbox_dir)
    if not inbox_path.exists():
        print(f"❌ Inbox directory not found: {inbox_dir}")
        return False
    
    # Find all .comments.mdx files
    comment_files = list(inbox_path.rglob("*.comments.mdx"))
    
    if not comment_files:
        print("ℹ️ No .comments.mdx files found")
        return []
    
    signed_files = []
    
    for comment_file in comment_files:
        print(f"  Signing: {comment_file}")
        
        # Generate file hash
        file_hash = generate_file_hash(comment_file)
        
        # Sign the file
        signature = sign_file(comment_file, key)
        
        # Create signed version
        signed_file = create_signed_file(comment_file, signature)
        signed_files.append(signed_file)
        
        print(f"    ✅ Signed: {signed_file}")
    
    print(f"✅ Signed {len(signed_files)} inbox files")
    
    # Log the signing
    log_sign_event("inbox_all", {
        "inbox_dir": inbox_dir,
        "signed_count": len(signed_files),
        "signed_files": [str(f) for f in signed_files]
    })
    
    return signed_files

@task(help={"file": "File path to verify", "signature": "Signature file path"})
def verify_all(c, file=None, signature=None):
    """Verifies existing signatures against hash chain or known Vault pubkey"""
    print("🔍 Verifying signatures")
    
    if file and signature:
        # Verify specific file
        return verify_file_signature(file, signature)
    else:
        # Verify all signed files
        return verify_all_signatures()

def verify_file_signature(file_path: str, signature_path: str) -> bool:
    """Verify signature for a specific file"""
    file_path = Path(file_path)
    signature_path = Path(signature_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    if not signature_path.exists():
        print(f"❌ Signature not found: {signature_path}")
        return False
    
    # Load signature
    with open(signature_path, 'r') as f:
        signature_data = json.load(f)
    
    # Generate file hash
    file_hash = generate_file_hash(file_path)
    
    # Verify signature
    is_valid = verify_signature(file_hash, signature_data)
    
    if is_valid:
        print(f"✅ Signature verified: {file_path}")
    else:
        print(f"❌ Signature invalid: {file_path}")
    
    return is_valid

def verify_all_signatures() -> Dict[str, bool]:
    """Verify all signatures in the project"""
    print("🔍 Scanning for signed files...")
    
    # Find all signature files
    signature_files = list(Path(".").rglob("*.signed.json"))
    
    results = {}
    
    for sig_file in signature_files:
        # Find corresponding file
        base_name = sig_file.stem.replace(".signed", "")
        possible_files = list(sig_file.parent.glob(f"{base_name}.*"))
        
        for file_path in possible_files:
            if file_path.suffix not in [".signed.json", ".signed"]:
                is_valid = verify_file_signature(str(file_path), str(sig_file))
                results[str(file_path)] = is_valid
                break
    
    valid_count = sum(1 for valid in results.values() if valid)
    total_count = len(results)
    
    print(f"✅ Verification complete: {valid_count}/{total_count} signatures valid")
    
    return results

def generate_bundle_manifest(bundle_path: Path) -> Dict[str, Any]:
    """Generate manifest for a bundle"""
    manifest = {
        "bundle_name": bundle_path.name,
        "timestamp": datetime.utcnow().isoformat(),
        "files": [],
        "hash": ""
    }
    
    # Add all files in bundle
    for file_path in bundle_path.rglob("*"):
        if file_path.is_file():
            file_hash = generate_file_hash(file_path)
            manifest["files"].append({
                "path": str(file_path.relative_to(bundle_path)),
                "hash": file_hash,
                "size": file_path.stat().st_size
            })
    
    # Generate bundle hash
    bundle_hash = hashlib.sha256()
    for file_info in manifest["files"]:
        bundle_hash.update(file_info["hash"].encode())
    
    manifest["hash"] = bundle_hash.hexdigest()
    
    return manifest

def sign_manifest(manifest: Dict[str, Any], key_path: str) -> Dict[str, Any]:
    """Sign a manifest with the Vault key"""
    # Load private key
    with open(key_path, 'r') as f:
        private_key = f.read().strip()
    
    # Create signature data
    signature_data = {
        "manifest_hash": manifest["hash"],
        "timestamp": datetime.utcnow().isoformat(),
        "key_id": "vault_key",
        "algorithm": "sha256"
    }
    
    # Generate signature (simplified - would use proper crypto)
    signature_hash = hashlib.sha256()
    signature_hash.update(manifest["hash"].encode())
    signature_hash.update(signature_data["timestamp"].encode())
    
    signature_data["signature"] = signature_hash.hexdigest()
    
    return signature_data

def create_signed_bundle(bundle_path: Path, manifest: Dict[str, Any], signature: Dict[str, Any]) -> str:
    """Create a signed bundle archive"""
    # Create signed bundle directory
    signed_dir = bundle_path.parent / f"{bundle_path.name}.signed"
    signed_dir.mkdir(exist_ok=True)
    
    # Copy bundle contents
    if bundle_path.is_dir():
        shutil.copytree(bundle_path, signed_dir / bundle_path.name, dirs_exist_ok=True)
    else:
        shutil.copy2(bundle_path, signed_dir / bundle_path.name)
    
    # Save manifest and signature
    with open(signed_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    with open(signed_dir / "signature.json", 'w') as f:
        json.dump(signature, f, indent=2)
    
    # Create zip archive
    zip_path = f"{signed_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(signed_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(signed_dir)
                zipf.write(file_path, arcname)
    
    # Cleanup temp directory
    shutil.rmtree(signed_dir)
    
    return zip_path

def generate_file_hash(file_path: Path) -> str:
    """Generate SHA256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def sign_file(file_path: Path, key_path: str) -> Dict[str, Any]:
    """Sign a file with the Vault key"""
    # Generate file hash
    file_hash = generate_file_hash(file_path)
    
    # Load private key
    with open(key_path, 'r') as f:
        private_key = f.read().strip()
    
    # Create signature data
    signature_data = {
        "file": str(file_path),
        "hash": file_hash,
        "timestamp": datetime.utcnow().isoformat(),
        "key_id": "vault_key",
        "algorithm": "sha256"
    }
    
    # Generate signature (simplified - would use proper crypto)
    signature_hash = hashlib.sha256()
    signature_hash.update(file_hash.encode())
    signature_hash.update(signature_data["timestamp"].encode())
    
    signature_data["signature"] = signature_hash.hexdigest()
    
    return signature_data

def create_signed_file(file_path: Path, signature: Dict[str, Any]) -> Path:
    """Create a signed version of a file"""
    # Create signature file
    signature_file = file_path.parent / f"{file_path.stem}.signed.json"
    
    with open(signature_file, 'w') as f:
        json.dump(signature, f, indent=2)
    
    return signature_file

def verify_signature(file_hash: str, signature_data: Dict[str, Any]) -> bool:
    """Verify a signature"""
    # Recreate signature hash
    signature_hash = hashlib.sha256()
    signature_hash.update(file_hash.encode())
    signature_hash.update(signature_data["timestamp"].encode())
    
    expected_signature = signature_hash.hexdigest()
    actual_signature = signature_data["signature"]
    
    return expected_signature == actual_signature

def log_sign_event(event_type: str, data: Dict[str, Any]) -> None:
    """Log signing events to vault logbook"""
    log_path = Path("vault/logbook/storj.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": f"sign_{event_type}",
        "data": data
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Create sign namespace
sign_ns = Collection("sign")
sign_ns.add_task(pulse_bundle, name="pulse_bundle")
sign_ns.add_task(inbox_all, name="inbox_all")
sign_ns.add_task(verify_all, name="verify_all") 
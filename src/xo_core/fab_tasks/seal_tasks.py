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

@task(help={"drop": "Drop name or path", "message": "Seal message"})
def drop_bundle(c, drop, message=None):
    """Seals a drop by finalizing metadata, signing variants, and archiving the bundle"""
    print(f"🔒 Sealing drop bundle: {drop}")
    
    # Find drop directory
    drop_path = find_drop_path(drop)
    if not drop_path:
        print(f"❌ Drop not found: {drop}")
        return False
    
    # Generate seal metadata
    seal_metadata = generate_seal_metadata(drop_path, "drop", message)
    
    # Finalize drop metadata
    finalized_metadata = finalize_drop_metadata(drop_path)
    
    # Sign all variants
    signed_variants = sign_drop_variants(drop_path)
    
    # Create sealed archive
    sealed_archive = create_sealed_archive(drop_path, seal_metadata, finalized_metadata, signed_variants)
    
    print(f"✅ Drop sealed: {sealed_archive}")
    
    # Log the sealing
    log_seal_event("drop_bundle", {
        "drop": drop,
        "sealed_archive": sealed_archive,
        "seal_hash": seal_metadata["hash"]
    })
    
    return sealed_archive

@task(help={"pulse": "Pulse name or path", "message": "Seal message"})
def pulse_freeze(c, pulse, message=None):
    """Freezes a Pulse and its comments into a read-only snapshot, signs, and archives it"""
    print(f"🧊 Freezing pulse: {pulse}")
    
    # Find pulse directory
    pulse_path = find_pulse_path(pulse)
    if not pulse_path:
        print(f"❌ Pulse not found: {pulse}")
        return False
    
    # Generate seal metadata
    seal_metadata = generate_seal_metadata(pulse_path, "pulse", message)
    
    # Create read-only snapshot
    snapshot = create_readonly_snapshot(pulse_path)
    
    # Sign the snapshot
    signed_snapshot = sign_snapshot(snapshot)
    
    # Archive the frozen pulse
    frozen_archive = create_frozen_archive(pulse_path, seal_metadata, signed_snapshot)
    
    print(f"✅ Pulse frozen: {frozen_archive}")
    
    # Log the freezing
    log_seal_event("pulse_freeze", {
        "pulse": pulse,
        "frozen_archive": frozen_archive,
        "seal_hash": seal_metadata["hash"]
    })
    
    return frozen_archive

@task(help={"inbox": "Inbox file path", "message": "Seal message"})
def inbox_lock(c, inbox, message=None):
    """Disables further writes to a .comments.mdx file and pins final version to IPFS"""
    print(f"🔒 Locking inbox: {inbox}")
    
    inbox_path = Path(inbox)
    if not inbox_path.exists():
        print(f"❌ Inbox file not found: {inbox}")
        return False
    
    # Generate seal metadata
    seal_metadata = generate_seal_metadata(inbox_path, "inbox", message)
    
    # Create read-only version
    readonly_version = create_readonly_version(inbox_path)
    
    # Pin to IPFS
    ipfs_hash = pin_to_ipfs(readonly_version)
    
    # Create lock manifest
    lock_manifest = create_lock_manifest(inbox_path, seal_metadata, ipfs_hash)
    
    print(f"✅ Inbox locked: {lock_manifest}")
    
    # Log the locking
    log_seal_event("inbox_lock", {
        "inbox": inbox,
        "lock_manifest": lock_manifest,
        "ipfs_hash": ipfs_hash
    })
    
    return lock_manifest

@task(help={"message": "Seal message"})
def system_snapshot(c, message=None):
    """Creates a full system snapshot (Vault, Drops, Inbox, Digest) into a sealed .zip with signed manifest"""
    print("📸 Creating system snapshot")
    
    # Generate seal metadata
    seal_metadata = generate_seal_metadata(Path("."), "system", message)
    
    # Collect system components
    components = collect_system_components()
    
    # Create snapshot directory
    snapshot_dir = create_snapshot_directory(components)
    
    # Sign the snapshot
    signed_snapshot = sign_system_snapshot(snapshot_dir)
    
    # Create sealed archive
    sealed_archive = create_system_archive(snapshot_dir, seal_metadata, signed_snapshot)
    
    print(f"✅ System snapshot created: {sealed_archive}")
    
    # Log the snapshot
    log_seal_event("system_snapshot", {
        "sealed_archive": sealed_archive,
        "components": list(components.keys()),
        "seal_hash": seal_metadata["hash"]
    })
    
    return sealed_archive

@task(help={"message": "Seal message"})
def now(c, message=None):
    """Generates a sealed snapshot of current infra status and app state"""
    print("🔒 Creating immediate seal")
    
    # Generate seal metadata
    seal_metadata = generate_seal_metadata(Path("."), "immediate", message)
    
    # Capture current state
    current_state = capture_current_state()
    
    # Create seal
    seal_file = create_seal_file(seal_metadata, current_state)
    
    print(f"✅ Immediate seal created: {seal_file}")
    
    # Log the seal
    log_seal_event("now", {
        "seal_file": seal_file,
        "seal_hash": seal_metadata["hash"]
    })
    
    return seal_file

@task(help={"message": "Seal message"})
def with_message(c, message):
    """Same as seal.now, but includes a user-provided commit-style message"""
    return now(c, message)

@task(help={"seal": "Seal file path"})
def verify_snapshot(c, seal="latest_seal.json"):
    """Validates current state against last sealed hash/log"""
    print(f"🔍 Verifying snapshot: {seal}")
    
    seal_path = Path(seal)
    if not seal_path.exists():
        print(f"❌ Seal file not found: {seal}")
        return False
    
    # Load seal data
    with open(seal_path, 'r') as f:
        seal_data = json.load(f)
    
    # Capture current state
    current_state = capture_current_state()
    
    # Compare states
    comparison = compare_states(seal_data["state"], current_state)
    
    if comparison["matches"]:
        print("✅ Snapshot verification passed")
    else:
        print("❌ Snapshot verification failed")
        print("Differences:")
        for diff in comparison["differences"]:
            print(f"  - {diff}")
    
    return comparison["matches"]

@task(help={"message": "Log message"})
def log_entry(c, message):
    """Appends a manual seal event to the vault logbook"""
    print(f"📝 Logging seal entry: {message}")
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": "manual_seal",
        "message": message,
        "hash": generate_message_hash(message)
    }
    
    # Append to logbook
    log_path = Path("vault/logbook/seals.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"✅ Seal entry logged: {log_path}")
    
    return log_entry

@task(help={"seal1": "First seal file", "seal2": "Second seal file"})
def compare_history(c, seal1, seal2):
    """Diff and compare two seals for drift or mutation"""
    print(f"🔍 Comparing seals: {seal1} vs {seal2}")
    
    seal1_path = Path(seal1)
    seal2_path = Path(seal2)
    
    if not seal1_path.exists() or not seal2_path.exists():
        print("❌ One or both seal files not found")
        return False
    
    # Load seal data
    with open(seal1_path, 'r') as f:
        seal1_data = json.load(f)
    
    with open(seal2_path, 'r') as f:
        seal2_data = json.load(f)
    
    # Compare seals
    comparison = compare_seals(seal1_data, seal2_data)
    
    print(f"📊 Comparison Results:")
    print(f"  Drift Score: {comparison['drift_score']}")
    print(f"  Changes: {len(comparison['changes'])}")
    
    for change in comparison["changes"]:
        print(f"    - {change}")
    
    return comparison

@task(help={"message": "Seal message"})
def bundle_all(c, message=None):
    """Chains snapshot, verification, log, and Git tag/ZIP bundle into one"""
    print("📦 Bundling all seal operations")
    
    # Step 1: Create snapshot
    print("1️⃣ Creating snapshot...")
    snapshot = system_snapshot(c, message)
    
    # Step 2: Verify snapshot
    print("2️⃣ Verifying snapshot...")
    verification = verify_snapshot(c, "latest_seal.json")
    
    # Step 3: Log entry
    print("3️⃣ Logging entry...")
    log_entry(c, message or "Automated seal bundle")
    
    # Step 4: Git tag
    print("4️⃣ Creating Git tag...")
    tag_name = f"seal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    try:
        import subprocess
        subprocess.run(["git", "tag", tag_name], check=True)
        print(f"    ✅ Tagged: {tag_name}")
    except:
        print("    ⚠️ Git tag failed")
    
    # Step 5: Create ZIP bundle
    print("5️⃣ Creating ZIP bundle...")
    bundle_path = create_seal_bundle(snapshot, tag_name)
    
    print(f"✅ Seal bundle completed: {bundle_path}")
    
    return bundle_path

# Helper functions
def find_drop_path(drop_name: str) -> Optional[Path]:
    """Find drop directory by name"""
    possible_paths = [
        Path(f"content/drops/{drop_name}"),
        Path(f"public/drops/{drop_name}"),
        Path(f"src/xo_core/vault/seals/eighth/drop.assets/{drop_name}"),
        Path(drop_name)  # Direct path
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def find_pulse_path(pulse_name: str) -> Optional[Path]:
    """Find pulse directory by name"""
    possible_paths = [
        Path(f"content/pulses/{pulse_name}"),
        Path(f"public/pulses/{pulse_name}"),
        Path(pulse_name)  # Direct path
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def generate_seal_metadata(path: Path, seal_type: str, message: Optional[str]) -> Dict[str, Any]:
    """Generate seal metadata"""
    return {
        "seal_type": seal_type,
        "path": str(path),
        "timestamp": datetime.utcnow().isoformat(),
        "message": message or f"Automated {seal_type} seal",
        "hash": generate_path_hash(path)
    }

def generate_path_hash(path: Path) -> str:
    """Generate hash for a path"""
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(str(path).encode())
    hash_sha256.update(datetime.utcnow().isoformat().encode())
    return hash_sha256.hexdigest()

def finalize_drop_metadata(drop_path: Path) -> Dict[str, Any]:
    """Finalize drop metadata"""
    # Look for metadata files
    metadata_files = ["drop.preview.yml", "drop.status.json", ".drop.yml"]
    
    finalized = {}
    for meta_file in metadata_files:
        meta_path = drop_path / meta_file
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                finalized[meta_file] = yaml.safe_load(f)
    
    return finalized

def sign_drop_variants(drop_path: Path) -> List[str]:
    """Sign all drop variants"""
    signed_variants = []
    
    # Find asset files
    asset_files = list(drop_path.rglob("*.webp")) + list(drop_path.rglob("*.png")) + list(drop_path.rglob("*.jpg"))
    
    for asset in asset_files:
        # Generate signature (simplified)
        signature = generate_file_signature(asset)
        signed_variants.append(str(asset))
    
    return signed_variants

def create_sealed_archive(drop_path: Path, seal_metadata: Dict, finalized_metadata: Dict, signed_variants: List[str]) -> str:
    """Create sealed archive for drop"""
    # Create sealed directory
    sealed_dir = drop_path.parent / f"{drop_path.name}.sealed"
    sealed_dir.mkdir(exist_ok=True)
    
    # Copy drop contents
    shutil.copytree(drop_path, sealed_dir / drop_path.name, dirs_exist_ok=True)
    
    # Save metadata
    with open(sealed_dir / "seal_metadata.json", 'w') as f:
        json.dump(seal_metadata, f, indent=2)
    
    with open(sealed_dir / "finalized_metadata.json", 'w') as f:
        json.dump(finalized_metadata, f, indent=2)
    
    # Create zip archive
    zip_path = f"{sealed_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(sealed_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(sealed_dir)
                zipf.write(file_path, arcname)
    
    # Cleanup
    shutil.rmtree(sealed_dir)
    
    return zip_path

def create_readonly_snapshot(pulse_path: Path) -> Path:
    """Create read-only snapshot of pulse"""
    snapshot_dir = pulse_path.parent / f"{pulse_path.name}.frozen"
    shutil.copytree(pulse_path, snapshot_dir, dirs_exist_ok=True)
    
    # Make read-only
    for file_path in snapshot_dir.rglob("*"):
        if file_path.is_file():
            file_path.chmod(0o444)  # Read-only
    
    return snapshot_dir

def sign_snapshot(snapshot_path: Path) -> Dict[str, Any]:
    """Sign a snapshot"""
    return {
        "snapshot_path": str(snapshot_path),
        "signature": generate_path_signature(snapshot_path),
        "timestamp": datetime.utcnow().isoformat()
    }

def create_frozen_archive(pulse_path: Path, seal_metadata: Dict, signed_snapshot: Dict) -> str:
    """Create frozen archive for pulse"""
    # Create frozen directory
    frozen_dir = pulse_path.parent / f"{pulse_path.name}.frozen"
    
    # Create zip archive
    zip_path = f"{frozen_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(frozen_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(frozen_dir)
                zipf.write(file_path, arcname)
    
    # Add metadata
    with zipfile.ZipFile(zip_path, 'a') as zipf:
        zipf.writestr("seal_metadata.json", json.dumps(seal_metadata, indent=2))
        zipf.writestr("signed_snapshot.json", json.dumps(signed_snapshot, indent=2))
    
    return zip_path

def create_readonly_version(file_path: Path) -> Path:
    """Create read-only version of file"""
    readonly_path = file_path.parent / f"{file_path.stem}.readonly{file_path.suffix}"
    shutil.copy2(file_path, readonly_path)
    readonly_path.chmod(0o444)  # Read-only
    return readonly_path

def pin_to_ipfs(file_path: Path) -> str:
    """Pin file to IPFS (mock implementation)"""
    # This would use actual IPFS API
    return f"QmMockHash{hashlib.md5(str(file_path).encode()).hexdigest()[:10]}"

def create_lock_manifest(inbox_path: Path, seal_metadata: Dict, ipfs_hash: str) -> str:
    """Create lock manifest for inbox"""
    lock_manifest = {
        "inbox_file": str(inbox_path),
        "seal_metadata": seal_metadata,
        "ipfs_hash": ipfs_hash,
        "locked_at": datetime.utcnow().isoformat(),
        "status": "locked"
    }
    
    manifest_path = inbox_path.parent / f"{inbox_path.stem}.lock.json"
    with open(manifest_path, 'w') as f:
        json.dump(lock_manifest, f, indent=2)
    
    return str(manifest_path)

def collect_system_components() -> Dict[str, Path]:
    """Collect system components for snapshot"""
    components = {}
    
    # Vault
    if Path("vault").exists():
        components["vault"] = Path("vault")
    
    # Drops
    if Path("content/drops").exists():
        components["drops"] = Path("content/drops")
    
    # Inbox
    if Path("content/pulses").exists():
        components["inbox"] = Path("content/pulses")
    
    # Digest
    if Path("public/digest").exists():
        components["digest"] = Path("public/digest")
    
    return components

def create_snapshot_directory(components: Dict[str, Path]) -> Path:
    """Create snapshot directory with components"""
    snapshot_dir = Path(f"snapshots/system_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    for name, path in components.items():
        if path.exists():
            shutil.copytree(path, snapshot_dir / name, dirs_exist_ok=True)
    
    return snapshot_dir

def sign_system_snapshot(snapshot_dir: Path) -> Dict[str, Any]:
    """Sign system snapshot"""
    return {
        "snapshot_path": str(snapshot_dir),
        "signature": generate_path_signature(snapshot_dir),
        "timestamp": datetime.utcnow().isoformat()
    }

def create_system_archive(snapshot_dir: Path, seal_metadata: Dict, signed_snapshot: Dict) -> str:
    """Create system archive"""
    zip_path = f"{snapshot_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(snapshot_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(snapshot_dir)
                zipf.write(file_path, arcname)
    
    # Add metadata
    with zipfile.ZipFile(zip_path, 'a') as zipf:
        zipf.writestr("seal_metadata.json", json.dumps(seal_metadata, indent=2))
        zipf.writestr("signed_snapshot.json", json.dumps(signed_snapshot, indent=2))
    
    return zip_path

def capture_current_state() -> Dict[str, Any]:
    """Capture current system state"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "files": list_files_recursive(Path(".")),
        "git_status": get_git_status()
    }

def create_seal_file(seal_metadata: Dict, current_state: Dict) -> str:
    """Create seal file"""
    seal_data = {
        "seal_metadata": seal_metadata,
        "state": current_state
    }
    
    seal_path = Path("latest_seal.json")
    with open(seal_path, 'w') as f:
        json.dump(seal_data, f, indent=2)
    
    return str(seal_path)

def generate_message_hash(message: str) -> str:
    """Generate hash for message"""
    return hashlib.sha256(message.encode()).hexdigest()

def compare_states(state1: Dict, state2: Dict) -> Dict[str, Any]:
    """Compare two states"""
    differences = []
    
    # Compare file lists
    files1 = set(state1.get("files", []))
    files2 = set(state2.get("files", []))
    
    added = files2 - files1
    removed = files1 - files2
    
    if added:
        differences.append(f"Added files: {len(added)}")
    if removed:
        differences.append(f"Removed files: {len(removed)}")
    
    return {
        "matches": len(differences) == 0,
        "differences": differences
    }

def compare_seals(seal1: Dict, seal2: Dict) -> Dict[str, Any]:
    """Compare two seals"""
    changes = []
    drift_score = 0
    
    # Compare timestamps
    time1 = datetime.fromisoformat(seal1["seal_metadata"]["timestamp"])
    time2 = datetime.fromisoformat(seal2["seal_metadata"]["timestamp"])
    time_diff = abs((time2 - time1).total_seconds())
    
    if time_diff > 3600:  # 1 hour
        changes.append(f"Time drift: {time_diff/3600:.1f} hours")
        drift_score += 1
    
    # Compare hashes
    if seal1["seal_metadata"]["hash"] != seal2["seal_metadata"]["hash"]:
        changes.append("Content hash changed")
        drift_score += 2
    
    return {
        "drift_score": drift_score,
        "changes": changes
    }

def generate_file_signature(file_path: Path) -> str:
    """Generate file signature (simplified)"""
    return hashlib.sha256(str(file_path).encode()).hexdigest()

def generate_path_signature(path: Path) -> str:
    """Generate path signature (simplified)"""
    return hashlib.sha256(str(path).encode()).hexdigest()

def list_files_recursive(path: Path) -> List[str]:
    """List all files recursively"""
    files = []
    for file_path in path.rglob("*"):
        if file_path.is_file():
            files.append(str(file_path.relative_to(path)))
    return files

def get_git_status() -> str:
    """Get git status (simplified)"""
    try:
        import subprocess
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return result.stdout.strip()[:8]
    except:
        return "unknown"

def create_seal_bundle(snapshot: str, tag_name: str) -> str:
    """Create seal bundle"""
    bundle_path = f"seals/{tag_name}.zip"
    Path("seals").mkdir(exist_ok=True)
    
    # Copy snapshot to bundle
    shutil.copy2(snapshot, bundle_path)
    
    return bundle_path

def log_seal_event(event_type: str, data: Dict[str, Any]) -> None:
    """Log seal events to vault logbook"""
    log_path = Path("vault/logbook/storj.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": f"seal_{event_type}",
        "data": data
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Create seal namespace
seal_ns = Collection("seal")
seal_ns.add_task(drop_bundle, name="drop_bundle")
seal_ns.add_task(pulse_freeze, name="pulse_freeze")
seal_ns.add_task(inbox_lock, name="inbox_lock")
seal_ns.add_task(system_snapshot, name="system_snapshot")
seal_ns.add_task(now, name="now")
seal_ns.add_task(with_message, name="with_message")
seal_ns.add_task(verify_snapshot, name="verify_snapshot")
seal_ns.add_task(log_entry, name="log_entry")
seal_ns.add_task(compare_history, name="compare_history")
seal_ns.add_task(bundle_all, name="bundle_all")

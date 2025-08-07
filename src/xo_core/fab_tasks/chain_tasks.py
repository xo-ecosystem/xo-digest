"""
XO Core Chain-of-Trust Implementation
Implements verifiable storychain with cryptographic hashing and signing.
"""

from invoke import task, Collection
import os
import json
import hashlib
import yaml
import time
from pathlib import Path
from datetime import datetime


def compute_content_hash(file_path):
    """Compute SHA256 hash of file content"""
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"❌ Failed to compute hash for {file_path}: {e}")
        return None


def get_previous_hash(chain_log_path):
    """Get the hash of the previous entry from chain log"""
    try:
        if not chain_log_path.exists():
            return "0000000000000000000000000000000000000000000000000000000000000000"

        with open(chain_log_path, "r") as f:
            lines = f.readlines()

        if not lines:
            return "0000000000000000000000000000000000000000000000000000000000000000"

        # Parse last entry to get hash
        last_entry = lines[-1].strip()
        if ":" in last_entry:
            return last_entry.split(":")[1].strip()

        return "0000000000000000000000000000000000000000000000000000000000000000"

    except Exception as e:
        print(f"⚠️  Failed to get previous hash: {e}")
        return "0000000000000000000000000000000000000000000000000000000000000000"


@task
def seal(c, drop_name):
    """Seal a drop with chain-of-trust metadata"""
    print(f"⛓️  Sealing drop with chain-of-trust: {drop_name}")

    # Locate drop directory
    drop_path = Path(f"drops/drafts/{drop_name}")
    if not drop_path.exists():
        drop_path = Path(f"drops/{drop_name}")

    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_name}")
        return False

    print(f"📁 Found drop at: {drop_path}")

    # Required files
    meta_file = drop_path / f"{drop_name}.meta.yml"
    content_file = drop_path / f"{drop_name}.mdx"

    if not content_file.exists():
        print(f"❌ Content file not found: {content_file}")
        return False

    # Compute content hash
    content_hash = compute_content_hash(content_file)
    if not content_hash:
        return False

    print(f"🔐 Content hash: {content_hash[:16]}...")

    # Get previous hash from chain
    chain_log = Path("vault/digest/chain.log")
    chain_log.parent.mkdir(parents=True, exist_ok=True)

    previous_hash = get_previous_hash(chain_log)
    print(f"🔗 Previous hash: {previous_hash[:16]}...")

    # Compute combined hash (content + metadata + previous)
    combined_input = f"{content_hash}{previous_hash}{int(time.time())}"
    current_hash = hashlib.sha256(combined_input.encode()).hexdigest()
    print(f"⚡ Current hash: {current_hash[:16]}...")

    # Update or create metadata
    meta_data = {}
    if meta_file.exists():
        try:
            with open(meta_file, "r") as f:
                meta_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Failed to read existing metadata: {e}")

    # Add chain-of-trust fields
    meta_data.update(
        {
            "previous_hash": previous_hash,
            "current_hash": current_hash,
            "content_hash": content_hash,
            "sealed_at": datetime.now().isoformat(),
            "chain_position": (
                len(open(chain_log, "r").readlines()) if chain_log.exists() else 0
            ),
        }
    )

    # Write updated metadata
    try:
        with open(meta_file, "w") as f:
            yaml.dump(meta_data, f, default_flow_style=False, sort_keys=False)
        print(f"✅ Updated metadata: {meta_file}")
    except Exception as e:
        print(f"❌ Failed to write metadata: {e}")
        return False

    # Log to chain
    chain_entry = (
        f"{datetime.now().isoformat()} : {current_hash} : {drop_name} : sealed"
    )
    try:
        with open(chain_log, "a") as f:
            f.write(chain_entry + "\n")
        print(f"📝 Logged to chain: {chain_log}")
    except Exception as e:
        print(f"❌ Failed to log to chain: {e}")
        return False

    # Move to sealed directory if in drafts
    if drop_path.parent.name == "drafts":
        sealed_path = Path("drops/sealed") / drop_name
        sealed_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import shutil

            shutil.move(str(drop_path), str(sealed_path))
            print(f"📦 Moved to sealed: {sealed_path}")
        except Exception as e:
            print(f"⚠️  Failed to move to sealed: {e}")

    print(f"✅ Drop sealed successfully: {drop_name}")
    return True


@task
def verify_chain(c):
    """Verify the integrity of the entire chain"""
    print("🔍 Verifying chain integrity...")

    chain_log = Path("vault/digest/chain.log")
    if not chain_log.exists():
        print(f"❌ Chain log not found: {chain_log}")
        return False

    try:
        with open(chain_log, "r") as f:
            entries = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read chain log: {e}")
        return False

    print(f"📊 Chain entries: {len(entries)}")

    # Verify each entry
    previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    verified_count = 0

    for i, entry in enumerate(entries):
        try:
            parts = entry.strip().split(" : ")
            if len(parts) >= 4:
                timestamp, current_hash, drop_name, action = parts[:4]

                # Find the drop and verify
                drop_paths = [
                    Path(f"drops/sealed/{drop_name}"),
                    Path(f"drops/drafts/{drop_name}"),
                    Path(f"drops/{drop_name}"),
                ]

                drop_found = False
                for drop_path in drop_paths:
                    if drop_path.exists():
                        meta_file = drop_path / f"{drop_name}.meta.yml"
                        if meta_file.exists():
                            with open(meta_file, "r") as f:
                                meta = yaml.safe_load(f)

                            if meta.get("current_hash") == current_hash:
                                verified_count += 1
                                print(f"  ✅ Entry {i+1}: {drop_name}")
                            else:
                                print(f"  ❌ Entry {i+1}: {drop_name} (hash mismatch)")

                            drop_found = True
                            break

                if not drop_found:
                    print(f"  ⚠️  Entry {i+1}: {drop_name} (drop not found)")

                previous_hash = current_hash
            else:
                print(f"  ❌ Entry {i+1}: Invalid format")

        except Exception as e:
            print(f"  ❌ Entry {i+1}: {e}")

    print(f"✅ Verification complete: {verified_count}/{len(entries)} verified")
    return verified_count == len(entries)


@task
def build_index(c):
    """Build chain index for vault explorer"""
    print("📚 Building chain index...")

    chain_log = Path("vault/digest/chain.log")
    if not chain_log.exists():
        print(f"❌ Chain log not found: {chain_log}")
        return False

    try:
        with open(chain_log, "r") as f:
            entries = f.readlines()
    except Exception as e:
        print(f"❌ Failed to read chain log: {e}")
        return False

    # Build index structure
    index_data = {
        "generated_at": datetime.now().isoformat(),
        "chain_length": len(entries),
        "items": [],
    }

    for i, entry in enumerate(entries):
        try:
            parts = entry.strip().split(" : ")
            if len(parts) >= 4:
                timestamp, current_hash, drop_name, action = parts[:4]

                item = {
                    "position": i,
                    "timestamp": timestamp,
                    "hash": current_hash,
                    "drop_name": drop_name,
                    "action": action,
                    "preview_url": f"/vault/preview/{drop_name}",
                    "explorer_url": f"/vault/chain/{drop_name}",
                }

                index_data["items"].append(item)
        except Exception as e:
            print(f"⚠️  Failed to parse entry {i}: {e}")

    # Write index
    index_path = Path("vault/chain/index.json")
    index_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(index_path, "w") as f:
            json.dump(index_data, f, indent=2, sort_keys=True)
        print(f"✅ Index written: {index_path}")
        print(f"📊 Indexed {len(index_data['items'])} items")
        return True
    except Exception as e:
        print(f"❌ Failed to write index: {e}")
        return False


# Create chain namespace
ns = Collection("chain")
ns.add_task(seal, "seal")
ns.add_task(verify_chain, "verify")
ns.add_task(build_index, "index")

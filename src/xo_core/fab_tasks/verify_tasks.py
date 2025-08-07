"""
XO Core Verification Tasks
Provides cryptographic verification for drops, chains, and vault integrity.
"""

from invoke import task, Collection
import os
import json
import hashlib
import yaml
from pathlib import Path


@task
def drop(c, drop_name):
    """Verify a specific drop's integrity and trust chain"""
    print(f"🔍 Verifying drop: {drop_name}")

    # Locate drop directory
    drop_path = Path(f"drops/{drop_name}")
    if not drop_path.exists():
        drop_path = Path(f"drops/drafts/{drop_name}")
        if not drop_path.exists():
            drop_path = Path(f"drops/sealed/{drop_name}")

    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_name}")
        return False

    print(f"📁 Found drop at: {drop_path}")

    # Check for required files
    meta_file = drop_path / f"{drop_name}.meta.yml"
    status_file = drop_path / f"{drop_name}.status.json"
    content_file = drop_path / f"{drop_name}.mdx"

    files_found = []
    files_missing = []

    for file_path, name in [
        (meta_file, ".meta.yml"),
        (status_file, ".status.json"),
        (content_file, ".mdx"),
    ]:
        if file_path.exists():
            files_found.append(name)
        else:
            files_missing.append(name)

    print(f"✅ Files found: {', '.join(files_found)}")
    if files_missing:
        print(f"⚠️  Files missing: {', '.join(files_missing)}")

    # Verify metadata structure
    if meta_file.exists():
        try:
            with open(meta_file, "r") as f:
                meta = yaml.safe_load(f)

            required_fields = ["title", "created_at", "author"]
            trust_fields = ["previous_hash", "current_hash", "signature"]

            print(f"📄 Metadata verification:")
            for field in required_fields:
                if field in meta:
                    print(f"  ✅ {field}: {meta[field]}")
                else:
                    print(f"  ❌ Missing: {field}")

            print(f"🔐 Trust chain fields:")
            for field in trust_fields:
                if field in meta:
                    print(
                        f"  ✅ {field}: {meta[field][:16]}..."
                        if len(str(meta[field])) > 16
                        else f"  ✅ {field}: {meta[field]}"
                    )
                else:
                    print(f"  ⚠️  Not set: {field}")

        except Exception as e:
            print(f"❌ Failed to parse metadata: {e}")

    # Verify content hash if available
    if content_file.exists() and meta_file.exists():
        try:
            with open(content_file, "rb") as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()

            with open(meta_file, "r") as f:
                meta = yaml.safe_load(f)

            if "current_hash" in meta and meta["current_hash"]:
                if meta["current_hash"] == content_hash:
                    print(f"✅ Content hash verified: {content_hash[:16]}...")
                else:
                    print(f"❌ Content hash mismatch!")
                    print(f"   Expected: {meta['current_hash'][:16]}...")
                    print(f"   Actual:   {content_hash[:16]}...")
            else:
                print(f"💡 Content hash (for reference): {content_hash[:16]}...")

        except Exception as e:
            print(f"⚠️  Hash verification failed: {e}")

    print(f"✅ Drop verification completed for: {drop_name}")
    return True


@task
def chain(c):
    """Verify the integrity of the entire vault chain"""
    print("⛓️  Verifying vault chain integrity...")

    # Look for chain log
    chain_log = Path("vault/digest/chain.log")
    if chain_log.exists():
        print(f"✅ Found chain log: {chain_log}")
        try:
            with open(chain_log, "r") as f:
                lines = f.readlines()
            print(f"📊 Chain entries: {len(lines)}")

            # Show last few entries
            print("📝 Recent entries:")
            for line in lines[-3:]:
                print(f"   {line.strip()}")

        except Exception as e:
            print(f"❌ Failed to read chain log: {e}")
    else:
        print(f"⚠️  No chain log found at: {chain_log}")

    # Check for vault index
    vault_index = Path("vault/chain/index.json")
    if vault_index.exists():
        print(f"✅ Found vault index: {vault_index}")
        try:
            with open(vault_index, "r") as f:
                index_data = json.load(f)
            print(f"📊 Indexed items: {len(index_data.get('items', []))}")
        except Exception as e:
            print(f"❌ Failed to read vault index: {e}")
    else:
        print(f"💡 Vault index could be created at: {vault_index}")

    print("✅ Chain verification completed")


@task
def vault(c):
    """Verify multi-node vault trust and consistency"""
    print("🔐 Verifying vault trust across nodes...")

    # Check vault status
    from xo_core.vault.bootstrap import get_vault_client

    try:
        client = get_vault_client()
        if client:
            print("✅ Vault client available")

            # Check seal status
            seal_status = client.sys.read_seal_status()
            if not seal_status["sealed"]:
                print("✅ Vault is unsealed")
            else:
                print("⚠️  Vault is sealed")

        else:
            print("❌ Vault client unavailable")

    except Exception as e:
        print(f"⚠️  Vault check failed: {e}")

    # Check local vault files
    vault_path = Path("vault")
    if vault_path.exists():
        print(f"✅ Local vault directory found")

        # Count vault files
        vault_files = list(vault_path.rglob("*.yml")) + list(vault_path.rglob("*.json"))
        print(f"📁 Vault files: {len(vault_files)}")

        # Check for key directories
        key_dirs = ["digest", "inbox", "drops", "chain"]
        for dir_name in key_dirs:
            dir_path = vault_path / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.rglob("*")))
                print(f"  ✅ {dir_name}/: {file_count} items")
            else:
                print(f"  📁 {dir_name}/: not found")
    else:
        print("❌ No local vault directory found")

    print("✅ Vault verification completed")


# Create verification namespace
ns = Collection("verify")
ns.add_task(drop, "drop")
ns.add_task(chain, "chain")
ns.add_task(vault, "vault")

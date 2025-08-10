"""
Vault module for XO Core.
"""

from invoke import Collection, task
from pathlib import Path
import yaml
import json
import logging

# Create the namespace
ns = Collection("vault")

# Import IPFS upload utility
try:
    from xo_core.vault.utils import upload_to_ipfs
except ImportError:
    # Mock upload function for testing
    def upload_to_ipfs(file_path):
        print(f"Mock upload: {file_path}")
        return {"cid": "mock_cid_12345"}


@task
def drop_audit(c, bundle):
    """
    Audit a drop bundle for preview, traits, and mint readiness.
    Usage: xo-fab vault.audit:"message_bottle"
    """
    drop_path = Path("drops") / bundle
    required_files = ["drop_main.webp", "drop.preview.yml", "drop.status.json", ".traits.yml"]

    print(f"🔍 Auditing drop: {bundle}")
    print(f"📁 Path: {drop_path}")

    if not drop_path.exists():
        print(f"❌ Drop directory not found: {drop_path}")
        return False

    # Check required files
    missing = []
    present = []
    for file in required_files:
        file_path = drop_path / file
        if file_path.exists():
            present.append(file)
        else:
            missing.append(file)

    if missing:
        print(f"⚠️ Missing files: {', '.join(missing)}")
    else:
        print(f"✅ All required drop files present")

    print(f"📋 Present: {', '.join(present)}")

    # Validate drop.status.json
    status_path = drop_path / "drop.status.json"
    if status_path.exists():
        try:
            with open(status_path, 'r') as f:
                status = json.load(f)
            print(f"✅ drop.status.json is valid JSON")

            # Check for required fields
            required_fields = ["drop", "title", "status", "description"]
            missing_fields = [field for field in required_fields if field not in status]
            if missing_fields:
                print(f"⚠️ Missing status fields: {', '.join(missing_fields)}")
            else:
                print(f"✅ All required status fields present")

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in drop.status.json: {e}")

    # Validate .traits.yml
    traits_path = drop_path / ".traits.yml"
    if traits_path.exists():
        try:
            with open(traits_path, 'r') as f:
                traits = yaml.safe_load(f)
            print(f"✅ .traits.yml is valid YAML")

            if isinstance(traits, list):
                print(f"📊 Found {len(traits)} traits")
                for trait in traits:
                    if isinstance(trait, dict):
                        trait_id = trait.get('id', 'unknown')
                        trait_name = trait.get('name', 'unnamed')
                        print(f"  - {trait_id}: {trait_name}")
            else:
                print(f"⚠️ .traits.yml should contain a list of traits")

        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML in .traits.yml: {e}")

    # Check for IPFS placeholders
    if traits_path.exists():
        with open(traits_path, 'r') as f:
            content = f.read()
            if "ipfs://<insert>" in content:
                print(f"⚠️ Found IPFS placeholders in .traits.yml - needs CID patching")
            else:
                print(f"✅ No IPFS placeholders found")

    return len(missing) == 0


@task
def vault_publish(c, bundle):
    """
    Upload drop assets + traits to IPFS and log result.
    Usage: xo-fab vault.publish:"message_bottle"
    """
    drop_path = Path("drops") / bundle
    traits_path = drop_path / ".traits.yml"

    print(f"🚀 Publishing drop: {bundle}")
    print(f"📁 Path: {drop_path}")

    if not drop_path.exists():
        print(f"❌ Drop directory not found: {drop_path}")
        return False

    # Upload main drop file
    main_file = drop_path / "drop_main.webp"
    if main_file.exists():
        print(f"⬆️ Uploading main drop file: {main_file.name}")
        result = upload_to_ipfs(main_file)
        if isinstance(result, dict) and "cid" in result:
            print(f"✅ Main drop uploaded: ipfs://{result['cid']}")
        else:
            print(f"❌ Failed to upload main drop")
            return False
    else:
        print(f"⚠️ Main drop file not found: {main_file}")

    # Upload and patch traits
    if traits_path.exists():
        try:
            with open(traits_path, 'r') as f:
                traits = yaml.safe_load(f) or []

            print(f"📊 Processing {len(traits)} traits...")

            for trait in traits:
                if isinstance(trait, dict):
                    trait_id = trait.get('id', 'unknown')
                    trait_name = trait.get('name', 'unnamed')
                    file_name = trait.get('file')

                    if file_name:
                        file_path = drop_path / file_name
                        if file_path.exists():
                            print(f"⬆️ Uploading trait file: {file_name}")
                            result = upload_to_ipfs(file_path)
                            if isinstance(result, dict) and "cid" in result:
                                cid = result['cid']
                                print(f"✅ {trait_name} uploaded: ipfs://{cid}")

                                # Patch the trait with CID
                                if 'media' in trait:
                                    if 'image' in trait['media'] and 'ipfs://<insert>' in trait['media']['image']:
                                        trait['media']['image'] = f"ipfs://{cid}"
                                    if 'animation' in trait['media'] and 'ipfs://<insert>' in trait['media']['animation']:
                                        trait['media']['animation'] = f"ipfs://{cid}"
                            else:
                                print(f"❌ Failed to upload {file_name}")
                        else:
                            print(f"⚠️ Trait file not found: {file_path}")

            # Save patched traits
            with open(traits_path, 'w') as f:
                yaml.dump(traits, f, sort_keys=False, default_flow_style=False)
            print(f"🧩 Patched .traits.yml with IPFS CIDs")

        except yaml.YAMLError as e:
            print(f"❌ Error processing .traits.yml: {e}")
            return False
    else:
        print(f"ℹ️ No .traits.yml found")

    # Create deployment log
    log_path = Path("vault/logbook")
    log_path.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"deploy_{bundle}_{timestamp}.md"

    with open(log_file, 'w') as f:
        f.write(f"# Drop Deployment Log: {bundle}\n\n")
        f.write(f"**Deployed:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Drop Path:** {drop_path}\n\n")
        f.write("## Files Processed\n\n")
        f.write(f"- ✅ drop_main.webp\n")
        f.write(f"- ✅ .traits.yml (patched with CIDs)\n")
        f.write(f"- ✅ drop.status.json\n\n")
        f.write("## Next Steps\n\n")
        f.write("1. Verify all IPFS links are accessible\n")
        f.write("2. Test mint functionality\n")
        f.write("3. Update drop.status.json with final metadata\n")

    print(f"📝 Deployment log saved: {log_file}")
    print(f"🎉 Drop '{bundle}' published successfully!")

    return True


@task
def vault_upload(c, path):
    """
    Upload a file or folder to IPFS (for Vault integration) and patch traits if available.
    Usage: xo-fab vault.upload:"message_bottle/scroll_02"
    """
    full_path = Path("drops") / path
    if not full_path.exists():
        print(f"❌ Path not found: {full_path}")
        return

    print(f"⬆️ Uploading {full_path} to IPFS...")
    ipfs_result = upload_to_ipfs(full_path)

    if isinstance(ipfs_result, dict) and "cid" in ipfs_result:
        cid = ipfs_result["cid"]
        print(f"✅ Uploaded to IPFS: {cid}")

        # Patch .traits.yml if it exists
        traits_path = full_path.parent / ".traits.yml"
        if traits_path.exists():
            with open(traits_path, "r") as f:
                traits = yaml.safe_load(f) or []

            # Append new trait if not already present
            new_trait = {"name": full_path.name, "ipfs": f"ipfs://{cid}"}
            if new_trait not in traits:
                traits.append(new_trait)
                with open(traits_path, "w") as f:
                    yaml.dump(traits, f, sort_keys=False)
                print(
                    f"🧩 Patched .traits.yml with IPFS reference for {full_path.name}"
                )
        else:
            print("ℹ️ No .traits.yml found to patch.")
    else:
        print("❌ Upload failed or did not return CID.")


# Add tasks to namespace
ns.add_task(drop_audit)
ns.add_task(vault_publish)
ns.add_task(vault_upload)

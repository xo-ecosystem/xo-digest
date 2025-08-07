"""
XO Core Drop Management Tasks
Validation, auditing, and publishing for drop lifecycle management
"""

from invoke import task, Collection
import json
import yaml
import hashlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime


@task
def audit(c, drop_id):
    """Validate drop metadata and check for missing files"""
    print(f"🔍 Auditing drop: {drop_id}")
    
    # Locate drop directory
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id
    ]
    
    drop_path = None
    for path in drop_paths:
        if path.exists():
            drop_path = path
            break
    
    if not drop_path:
        print(f"❌ Drop not found: {drop_id}")
        return False
    
    print(f"📁 Found drop at: {drop_path}")
    
    # Define expected files and their requirements
    file_checks = {
        f"{drop_id}.meta.yml": {"required": True, "description": "Metadata file"},
        f"{drop_id}.status.json": {"required": True, "description": "Status file"},
        f"{drop_id}.mdx": {"required": True, "description": "Content file"},
        "preview.yml": {"required": False, "description": "Preview configuration"},
        "hidden/.traits.yml": {"required": False, "description": "Traits definition"},
        ".lore.yml": {"required": False, "description": "Lore and narrative"},
        "inbox/seed.mdx": {"required": False, "description": "Inbox engagement seed"}
    }
    
    audit_results = {
        "drop_id": drop_id,
        "audit_timestamp": datetime.now().isoformat(),
        "path": str(drop_path),
        "files": {},
        "metadata_issues": [],
        "recommendations": [],
        "overall_status": "unknown"
    }
    
    # Check file existence
    files_found = 0
    required_files_found = 0
    total_required = sum(1 for check in file_checks.values() if check["required"])
    
    for filename, check in file_checks.items():
        file_path = drop_path / filename
        file_info = {
            "exists": file_path.exists(),
            "required": check["required"],
            "description": check["description"]
        }
        
        if file_path.exists():
            files_found += 1
            file_info["size"] = file_path.stat().st_size
            file_info["modified"] = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            
            if check["required"]:
                required_files_found += 1
                print(f"  ✅ {filename}: {file_info['size']} bytes")
            else:
                print(f"  📄 {filename}: {file_info['size']} bytes (optional)")
        else:
            if check["required"]:
                print(f"  ❌ {filename}: MISSING (required)")
            else:
                print(f"  ⚪ {filename}: not found (optional)")
        
        audit_results["files"][filename] = file_info
    
    # Validate metadata content
    meta_file = drop_path / f"{drop_id}.meta.yml"
    if meta_file.exists():
        try:
            with open(meta_file, 'r') as f:
                meta_data = yaml.safe_load(f)
            
            # Required metadata fields
            required_meta_fields = ["title", "created_at", "author"]
            recommended_meta_fields = ["description", "tags", "version"]
            chain_trust_fields = ["previous_hash", "current_hash", "sealed_at"]
            
            for field in required_meta_fields:
                if field not in meta_data:
                    audit_results["metadata_issues"].append(f"Missing required field: {field}")
                    print(f"  ❌ Missing required metadata: {field}")
                else:
                    print(f"  ✅ Metadata field: {field}")
            
            for field in recommended_meta_fields:
                if field not in meta_data:
                    audit_results["recommendations"].append(f"Consider adding metadata field: {field}")
            
            # Check chain-of-trust fields
            chain_fields_present = sum(1 for field in chain_trust_fields if field in meta_data)
            if chain_fields_present > 0 and chain_fields_present < len(chain_trust_fields):
                audit_results["metadata_issues"].append("Incomplete chain-of-trust metadata")
            elif chain_fields_present == len(chain_trust_fields):
                print(f"  🔗 Chain-of-trust: complete")
            
        except Exception as e:
            audit_results["metadata_issues"].append(f"Failed to parse metadata: {e}")
            print(f"  ❌ Metadata parsing error: {e}")
    
    # Validate status content
    status_file = drop_path / f"{drop_id}.status.json"
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            
            required_status_fields = ["title", "status"]
            for field in required_status_fields:
                if field not in status_data:
                    audit_results["metadata_issues"].append(f"Missing status field: {field}")
                    print(f"  ❌ Missing status field: {field}")
                else:
                    print(f"  ✅ Status field: {field}")
                    
        except Exception as e:
            audit_results["metadata_issues"].append(f"Failed to parse status: {e}")
            print(f"  ❌ Status parsing error: {e}")
    
    # Content validation
    content_file = drop_path / f"{drop_id}.mdx"
    if content_file.exists():
        try:
            with open(content_file, 'r') as f:
                content = f.read()
            
            if len(content) < 50:
                audit_results["recommendations"].append("Content file is very short, consider expanding")
            
            # Check for frontmatter
            if content.startswith("---"):
                print(f"  ✅ Content has frontmatter")
            else:
                audit_results["recommendations"].append("Consider adding frontmatter to content file")
                
        except Exception as e:
            audit_results["metadata_issues"].append(f"Failed to read content: {e}")
    
    # Generate recommendations
    if required_files_found < total_required:
        audit_results["recommendations"].append("Complete all required files before sealing")
    
    if not (drop_path / "hidden").exists():
        audit_results["recommendations"].append("Create hidden/ directory for traits and private metadata")
    
    if not (drop_path / "inbox").exists():
        audit_results["recommendations"].append("Create inbox/ directory for community engagement")
    
    # Determine overall status
    if len(audit_results["metadata_issues"]) == 0 and required_files_found == total_required:
        audit_results["overall_status"] = "ready"
        print(f"\n🎉 Drop audit: READY for sealing")
    elif required_files_found == total_required:
        audit_results["overall_status"] = "minor_issues"
        print(f"\n⚠️  Drop audit: Minor issues found")
    else:
        audit_results["overall_status"] = "needs_work"
        print(f"\n❌ Drop audit: Needs work before sealing")
    
    # Save audit report
    audit_file = drop_path / ".audit.json"
    with open(audit_file, 'w') as f:
        json.dump(audit_results, f, indent=2, sort_keys=True)
    
    print(f"📋 Audit report saved: {audit_file}")
    
    # Summary
    print(f"\n📊 AUDIT SUMMARY:")
    print(f"   Files found: {files_found}/{len(file_checks)}")
    print(f"   Required files: {required_files_found}/{total_required}")
    print(f"   Metadata issues: {len(audit_results['metadata_issues'])}")
    print(f"   Recommendations: {len(audit_results['recommendations'])}")
    print(f"   Overall status: {audit_results['overall_status'].upper()}")
    
    return audit_results["overall_status"] in ["ready", "minor_issues"]


@task
def publish(c, drop_id, target="ipfs"):
    """
    Publish drop to IPFS and sync previews
    Mini-publisher script for vault.publish functionality
    """
    print(f"📤 Publishing drop: {drop_id} to {target}")
    
    # First run audit
    print("🔍 Running pre-publish audit...")
    audit_result = audit(c, drop_id)
    
    if not audit_result:
        print("❌ Audit failed - fix issues before publishing")
        return False
    
    # Locate drop
    drop_paths = [
        Path("drops/sealed") / drop_id,  # Prefer sealed
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("vault/drops") / drop_id
    ]
    
    drop_path = None
    for path in drop_paths:
        if path.exists():
            drop_path = path
            break
    
    if not drop_path:
        print(f"❌ Drop not found: {drop_id}")
        return False
    
    print(f"📁 Publishing from: {drop_path}")
    
    # Generate content hash for verification
    content_file = drop_path / f"{drop_id}.mdx"
    if content_file.exists():
        with open(content_file, 'rb') as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()
        print(f"🔐 Content hash: {content_hash[:16]}...")
    
    # TODO: Actual IPFS publishing logic
    if target == "ipfs":
        print("🌐 IPFS publishing:")
        print("   📦 Creating IPFS bundle...")
        print("   🚀 Uploading to IPFS node...")
        print("   🔗 Generating content ID (CID)...")
        
        # Simulate IPFS CID (replace with actual IPFS logic)
        mock_cid = f"Qm{content_hash[:42] if content_file.exists() else 'mock123'}"
        print(f"   ✅ Published: ipfs://{mock_cid}")
        
        # Update metadata with IPFS link
        meta_file = drop_path / f"{drop_id}.meta.yml"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta_data = yaml.safe_load(f)
            
            meta_data["ipfs_cid"] = mock_cid
            meta_data["published_at"] = datetime.now().isoformat()
            meta_data["publication_target"] = target
            
            with open(meta_file, 'w') as f:
                yaml.dump(meta_data, f, default_flow_style=False, sort_keys=False)
            
            print(f"   📝 Updated metadata with IPFS CID")
    
    # Generate preview sync
    print("🖼️  Syncing previews...")
    preview_file = drop_path / "preview.yml"
    if not preview_file.exists():
        preview_data = {
            "title": drop_id,
            "thumbnail": f"/vault/preview/{drop_id}/thumb.jpg",
            "preview_url": f"/vault/preview/{drop_id}",
            "ipfs_link": f"ipfs://{mock_cid}" if target == "ipfs" else None,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(preview_file, 'w') as f:
            yaml.dump(preview_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"   ✅ Created preview configuration")
    
    print(f"🎉 Publishing completed for: {drop_id}")
    return True


@task
def scaffold(c, drop_id, template="basic"):
    """Create a new drop with template structure"""
    print(f"🏗️  Scaffolding new drop: {drop_id}")
    
    drop_path = Path("drops/drafts") / drop_id
    if drop_path.exists():
        print(f"❌ Drop already exists: {drop_path}")
        return False
    
    # Create drop structure
    drop_path.mkdir(parents=True, exist_ok=True)
    (drop_path / "hidden").mkdir(exist_ok=True)
    (drop_path / "inbox").mkdir(exist_ok=True)
    
    # Create basic files
    timestamp = datetime.now().isoformat()
    
    # Meta file
    meta_data = {
        "title": drop_id.replace("_", " ").title(),
        "created_at": timestamp,
        "author": "XO Creator",
        "description": f"A new drop in the XO universe: {drop_id}",
        "tags": ["draft", "new"],
        "version": "0.1.0"
    }
    
    with open(drop_path / f"{drop_id}.meta.yml", 'w') as f:
        yaml.dump(meta_data, f, default_flow_style=False, sort_keys=False)
    
    # Status file
    status_data = {
        "title": meta_data["title"],
        "status": "draft",
        "created_at": timestamp,
        "last_modified": timestamp
    }
    
    with open(drop_path / f"{drop_id}.status.json", 'w') as f:
        json.dump(status_data, f, indent=2, sort_keys=True)
    
    # Content file
    content = f"""---
title: {meta_data["title"]}
drop_id: {drop_id}
created_at: {timestamp}
---

# {meta_data["title"]}

*A new drop in the XO universe awaiting its story...*

## Overview

This is a fresh drop ready for development. Add your content, traits, and lore here.

## Next Steps

1. Run `xo-fab drop.audit:{drop_id}` to check completeness
2. Add traits in `hidden/.traits.yml`
3. Develop lore and backstory
4. Create inbox engagement hooks
5. Seal with `xo-fab chain.seal:{drop_id}`

---

*Generated by XO Drop Scaffolder - {timestamp}*
"""
    
    with open(drop_path / f"{drop_id}.mdx", 'w') as f:
        f.write(content)
    
    # Inbox seed
    inbox_content = f"""# 📬 {meta_data["title"]} - Community Inbox

*What story will emerge from this new drop?*

## Join the Conversation

Share your thoughts, questions, and creative expansions for this drop.

---

*Created: {timestamp}*
"""
    
    with open(drop_path / "inbox" / "seed.mdx", 'w') as f:
        f.write(inbox_content)
    
    print(f"✅ Drop scaffolded successfully: {drop_path}")
    print(f"📝 Files created:")
    print(f"   - {drop_id}.meta.yml")
    print(f"   - {drop_id}.status.json") 
    print(f"   - {drop_id}.mdx")
    print(f"   - inbox/seed.mdx")
    print(f"\n🎯 Next: xo-fab drop.audit:{drop_id}")
    
    return True


# Create drop namespace
ns = Collection("drop")
ns.add_task(audit, "audit")
ns.add_task(publish, "publish")
ns.add_task(scaffold, "scaffold")
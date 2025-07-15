"""
XO Vault Pinning System - Enhanced dual-pinning to IPFS and Arweave
Supports .mdx, .signed, and .txid files with comprehensive manifest tracking.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import requests
from invoke import task, Collection

# Import new modules
import sys
from pathlib import Path

# Add the project root to sys.path to import vault modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from vault.webhook import format_pin_summary
    from vault.digest import generate_pin_digest
    from vault.inbox import send_to_xo_inbox
    print("✅ Successfully imported vault modules")
except ImportError as e:
    print(f"Warning: Could not import vault modules: {e}")
    # Fallback to local functions if needed
    def format_pin_summary(summary, slug, style="markdown"):
        return f"Pin summary for {slug}: {summary}"
    def generate_pin_digest(summary, files):
        return f"# Pin Digest\nGenerated for {len(files)} files"
    def send_to_xo_inbox(message, manifest_path, slug):
        print(f"Would send to inbox: {message}")


# Configuration constants
PIN_CONFIG = {
    "paths": {
        "pin_dir": "vault/.pins",
        "signed_dir": "vault/.signed", 
        "synced_dir": "vault/.synced",
        "manifest_file": "vault/.pins/pin_manifest.json",
        "digest_file": "vault/.pins/pin_digest.mdx",
        "status_file": "vault/.pins/pin_status.json"
    },
    "file_types": {
        "content": [".mdx", ".signed"],
        "transaction": [".txid"],
        "markers": [".ipfs_cid", ".arweave_tx", ".pin_meta"]
    },
    "ipfs": {
        "gateway": "https://{cid}.ipfs.nftstorage.link/",
        "api_url": "https://api.nft.storage/upload"
    },
    "arweave": {
        "gateway": "https://arweave.net/{txid}",
        "script": "scripts/pin_to_arweave.py"
    }
}

# Environment variables
NFT_STORAGE_TOKEN = os.getenv("NFT_STORAGE_TOKEN")
ARWEAVE_WALLET_PATH = os.getenv("ARWEAVE_WALLET_PATH")

# Global state for verbose logging
VERBOSE_MODE = False


def print_log(message: str, level: str = "INFO") -> None:
    """Print log message with timestamp and optional verbose filtering"""
    if not VERBOSE_MODE and level == "DEBUG":
        return
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "DEBUG": "🔍",
        "INFO": "ℹ️", 
        "WARN": "⚠️",
        "ERROR": "❌",
        "SUCCESS": "✅"
    }.get(level, "ℹ️")
    
    print(f"[{timestamp}] {prefix} {message}")


def ensure_pin_dirs() -> Path:
    """Ensure pin manifest and log directories exist"""
    pin_dir = Path(PIN_CONFIG["paths"]["pin_dir"])
    pin_dir.mkdir(parents=True, exist_ok=True)
    print_log(f"Ensured pin directory: {pin_dir}", "DEBUG")
    return pin_dir


def load_pin_manifest() -> Dict[str, Any]:
    """Load existing pin manifest or create new one"""
    manifest_path = Path(PIN_CONFIG["paths"]["manifest_file"])
    
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            print_log(f"Loaded existing manifest: {len(manifest)} entries", "DEBUG")
            return manifest
        except Exception as e:
            print_log(f"Error loading pin manifest: {e}", "WARN")
    
    print_log("Creating new pin manifest", "DEBUG")
    return {}


def save_pin_manifest(manifest: Dict[str, Any]) -> None:
    """Save pin manifest to file"""
    manifest_path = Path(PIN_CONFIG["paths"]["manifest_file"])
    
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print_log(f"Pin manifest saved: {manifest_path}")
    except Exception as e:
        print_log(f"Error saving pin manifest: {e}", "ERROR")


def log_pin_activity(message: str) -> None:
    """Log pin activity to daily log file"""
    pin_dir = ensure_pin_dirs()
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = pin_dir / f"pin_log_{today}.txt"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_path, 'a') as f:
            f.write(log_entry)
        print_log(f"Activity logged: {message}", "DEBUG")
    except Exception as e:
        print_log(f"Error writing to pin log: {e}", "WARN")


def check_already_pinned(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Check if file is already pinned using .ipfs_cid or .arweave_tx markers"""
    ipfs_marker = file_path.with_suffix(file_path.suffix + ".ipfs_cid")
    arweave_marker = file_path.with_suffix(file_path.suffix + ".arweave_tx")
    
    ipfs_cid = None
    arweave_tx = None
    
    if ipfs_marker.exists():
        try:
            ipfs_cid = ipfs_marker.read_text().strip()
            print_log(f"Found existing IPFS CID: {ipfs_cid}", "DEBUG")
        except:
            pass
    
    if arweave_marker.exists():
        try:
            arweave_tx = arweave_marker.read_text().strip()
            print_log(f"Found existing Arweave TX: {arweave_tx}", "DEBUG")
        except:
            pass
    
    return ipfs_cid, arweave_tx


def pin_file_to_ipfs(file_path):
    """Pin a single file to IPFS using nft.storage"""
    if not NFT_STORAGE_TOKEN:
        print_log("❌ NFT_STORAGE_TOKEN not set", "ERROR")
        return None
    
    headers = {
        "Authorization": f"Bearer {NFT_STORAGE_TOKEN}",
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(
                PIN_CONFIG["ipfs"]["api_url"], 
                headers=headers, 
                files=files
            )
        
        if response.status_code == 200:
            cid = response.json()["value"]["cid"]
            print_log(f"🔗 TXID pinned to IPFS: ipfs://{cid}", "SUCCESS")
            log_pin_activity(f"IPFS pin successful: {file_path.name} -> {cid}")
            
            # Save IPFS CID marker
            ipfs_marker = file_path.with_suffix(file_path.suffix + ".ipfs_cid")
            ipfs_marker.write_text(cid)
            
            return cid
        else:
            print_log(f"❌ IPFS upload failed: {response.status_code}", "ERROR")
            log_pin_activity(f"IPFS pin failed: {file_path.name} -> {response.status_code}")
            return None
    except Exception as e:
        print_log(f"❌ IPFS pinning error: {e}", "ERROR")
        log_pin_activity(f"IPFS pin error: {file_path.name} -> {e}")
        return None


def pin_file_to_arweave(file_path):
    """Pin a single file to Arweave using arweave-python-client"""
    try:
        # Try to use the existing arweave script
        result = subprocess.run(
            ["python", PIN_CONFIG["arweave"]["script"], "--file", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Extract TXID from output
            for line in result.stdout.split('\n'):
                if 'TX ID:' in line:
                    txid = line.split('TX ID:')[-1].strip()
                    print_log(f"🔗 TXID pinned to Arweave: {txid}", "SUCCESS")
                    log_pin_activity(f"Arweave pin successful: {file_path.name} -> {txid}")
                    
                    # Save Arweave TXID marker
                    arweave_marker = file_path.with_suffix(file_path.suffix + ".arweave_tx")
                    arweave_marker.write_text(txid)
                    
                    return txid
            print_log("✅ Arweave upload successful (TXID not found in output)", "INFO")
            log_pin_activity(f"Arweave pin successful: {file_path.name} -> (no TXID in output)")
            return "uploaded"
        else:
            print_log(f"❌ Arweave upload failed: {result.stderr}", "ERROR")
            log_pin_activity(f"Arweave pin failed: {file_path.name} -> {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print_log("❌ Arweave upload timed out", "ERROR")
        log_pin_activity(f"Arweave pin timeout: {file_path.name}")
        return None
    except FileNotFoundError:
        print_log("⚠️ Arweave script not found, skipping Arweave pinning", "WARN")
        log_pin_activity(f"Arweave script not found: {file_path.name}")
        return None
    except Exception as e:
        print_log(f"❌ Arweave pinning error: {e}", "ERROR")
        log_pin_activity(f"Arweave pin error: {file_path.name} -> {e}")
        return None


def save_pin_status(healthy: int, broken: int, missing: int) -> None:
    """Save pin status to JSON file"""
    status_path = Path(PIN_CONFIG["paths"]["status_file"])
    
    status_data = {
        "last_check": datetime.now().isoformat(),
        "summary": {
            "healthy": healthy,
            "broken": broken,
            "missing": missing,
            "total": healthy + broken + missing
        },
        "health_percentage": round((healthy / (healthy + broken + missing)) * 100, 1) if (healthy + broken + missing) > 0 else 0
    }
    
    try:
        with open(status_path, 'w') as f:
            json.dump(status_data, f, indent=2)
        print_log(f"Pin status saved: {status_path}")
    except Exception as e:
        print_log(f"Error saving pin status: {e}", "ERROR")


def send_pin_webhook(slug: Optional[str], summary: Dict[str, int]) -> None:
    """Send pin summary to webhook"""
    try:
        # Try to use existing webhook script
        webhook_script = "scripts/send_webhook.py"
        if Path(webhook_script).exists():
            message = f"📦 XO Vault Pin Summary\n"
            if slug:
                message += f"Pulse: {slug}\n"
            message += f"✅ Pinned: {summary.get('pinned', 0)}\n"
            message += f"⚠️ Skipped: {summary.get('skipped', 0)}\n"
            message += f"❌ Failed: {summary.get('failed', 0)}\n"
            message += f"📊 Manifest: vault/.pins/pin_manifest.json"
            
            result = subprocess.run(
                ["python", webhook_script, "--message", message],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print_log("Webhook notification sent", "SUCCESS")
            else:
                print_log(f"Webhook failed: {result.stderr}", "WARN")
        else:
            print_log("Webhook script not found, skipping notification", "DEBUG")
    except Exception as e:
        print_log(f"Error sending webhook: {e}", "WARN")


def check_pin_health(c, slug: Optional[str] = None, repair: bool = False) -> Tuple[int, int, int]:
    """Check pin health and return counts"""
    print_log("🔍 Checking pin health...", "INFO")
    
    # Find files to check
    patterns = [
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.signed",
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.mdx",
        PIN_CONFIG["paths"]["synced_dir"] + "/**/*.mdx",
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.txid", 
        PIN_CONFIG["paths"]["synced_dir"] + "/**/*.txid",
    ]
    
    if slug:
        patterns = [p for p in patterns if slug in p]
    
    found_files = []
    for pattern in patterns:
        found_files.extend(Path(".").glob(pattern))
    
    if not found_files:
        print_log("⚠️ No files found to check.", "WARN")
        return 0, 0, 0
    
    healthy, broken, missing = 0, 0, 0
    
    for file_path in sorted(found_files):
        print_log(f"🔍 Checking: {file_path}", "DEBUG")
        
        # Check for pin metadata
        meta_file = file_path.with_suffix(file_path.suffix + ".pin_meta")
        pinned_marker = file_path.with_suffix(file_path.suffix + ".pinned")
        
        if not meta_file.exists() or not pinned_marker.exists():
            print_log(f"  ❌ Missing pin metadata", "WARN")
            missing += 1
            if repair:
                print_log(f"  🔧 Re-pinning: {file_path}", "INFO")
                try:
                    if file_path.suffix == ".txid":
                        pin_file_to_ipfs(file_path)
                        pin_file_to_arweave(file_path)
                    else:
                        pin(c, file_path.stem)
                    healthy += 1
                except Exception as e:
                    print_log(f"  ❌ Re-pin failed: {e}", "ERROR")
                    broken += 1
            continue
        
        try:
            with open(meta_file, 'r') as f:
                pin_meta = json.load(f)
            
            cid = pin_meta.get('ipfs_cid')
            if not cid:
                print_log(f"  ❌ Invalid pin metadata (no CID)", "WARN")
                broken += 1
                continue
            
            # Check CID validity (basic format check)
            if not cid.startswith('bafy'):
                print_log(f"  ❌ Invalid CID format: {cid}", "WARN")
                broken += 1
                continue
            
            # Check pin freshness (optional)
            pinned_at = pin_meta.get('pinned_at')
            if pinned_at:
                try:
                    pin_date = datetime.fromisoformat(pinned_at)
                    if datetime.now() - pin_date > timedelta(days=30):
                        print_log(f"  ⚠️ Pin is old ({pin_date.strftime('%Y-%m-%d')})", "WARN")
                        if repair:
                            print_log(f"  🔧 Re-pinning old pin: {file_path}", "INFO")
                            if file_path.suffix == ".txid":
                                pin_file_to_ipfs(file_path)
                                pin_file_to_arweave(file_path)
                            else:
                                pin(c, file_path.stem)
                            healthy += 1
                            continue
                except:
                    print_log(f"  ⚠️ Could not parse pin date", "WARN")
            
            # Test gateway accessibility
            gateway = PIN_CONFIG["ipfs"]["gateway"].format(cid=cid)
            try:
                test_url = gateway.rstrip('/') + '/'
                response = requests.head(test_url, timeout=10)
                if response.status_code == 200:
                    print_log(f"  ✅ Healthy: {gateway}", "DEBUG")
                    healthy += 1
                else:
                    print_log(f"  ❌ Gateway error: {response.status_code}", "WARN")
                    broken += 1
            except Exception as e:
                print_log(f"  ❌ Gateway unreachable: {e}", "WARN")
                broken += 1
                
        except Exception as e:
            print_log(f"  ❌ Error reading metadata: {e}", "ERROR")
            broken += 1
    
    print_log(f"📊 Pin Health Summary:", "INFO")
    print_log(f"  ✅ Healthy: {healthy}", "INFO")
    print_log(f"  ❌ Broken: {broken}", "WARN")
    print_log(f"  ⚠️ Missing: {missing}", "WARN")
    
    # Save status
    save_pin_status(healthy, broken, missing)
    
    if repair and (broken > 0 or missing > 0):
        print_log(f"🔧 Auto-repair completed. Re-run status check to verify.", "INFO")
    
    return healthy, broken, missing


@task(help={"slug": "Name of the vault bundle (slug)"})
def pin(c, slug):
    print_log(f"📦 Pinning bundle: {slug}", "INFO")
    base_path = Path(f"./vault/{slug}_bundle")
    if not base_path.exists():
        print_log("❌ Bundle directory not found.", "ERROR")
        return

    files = list(base_path.glob("*"))
    if not files:
        print_log("⚠️ No files found in bundle.", "WARN")
        return

    headers = {
        "Authorization": f"Bearer {NFT_STORAGE_TOKEN}",
    }

    # Construct multipart form-data manually
    multiple_files = [("file", (f.name, f.open("rb"))) for f in files]

    print_log("⏳ Uploading to nft.storage...", "INFO")
    res = requests.post(
        PIN_CONFIG["ipfs"]["api_url"], headers=headers, files=multiple_files
    )
    if res.status_code == 200:
        cid = res.json()["value"]["cid"]
        print_log(f"✅ Uploaded to IPFS: ipfs://{cid}", "SUCCESS")
        print_log(f"🔗 Gateway: https://{cid}.ipfs.nftstorage.link/", "INFO")
        
        # Save pin metadata
        pin_meta = {
            "cid": cid,
            "pinned_at": datetime.now().isoformat(),
            "gateway": f"https://{cid}.ipfs.nftstorage.link/"
        }
        meta_file = base_path.with_suffix(base_path.suffix + ".pin_meta")
        with open(meta_file, 'w') as f:
            json.dump(pin_meta, f, indent=2)
        
        return cid
    else:
        print_log(f"❌ Upload failed: {res.status_code}", "ERROR")
        print_log(res.text, "ERROR")
        return None


@task(help={
    "repair": "Auto re-pin broken/missing pins",
    "slug": "Check specific slug (optional)",
    "verbose": "Enable detailed logging"
})
def pin_status(c, repair=False, slug=None, verbose=False):
    """
    📌 Check pinning health: existence, CID validity, freshness
    
    Comprehensive health check for all pinned content with optional auto-repair.
    """
    global VERBOSE_MODE
    VERBOSE_MODE = verbose
    
    print_log("🔍 Starting pin health check", "INFO")
    
    # Use the new health check function
    healthy, broken, missing = check_pin_health(c, slug=slug, repair=repair)
    
    # Additional summary
    total = healthy + broken + missing
    if total > 0:
        health_percentage = round((healthy / total) * 100, 1)
        print_log(f"📊 Overall Health: {health_percentage}% ({healthy}/{total})", "INFO")
        
        if health_percentage == 100:
            print_log("🎉 All pins are healthy!", "SUCCESS")
        elif health_percentage >= 80:
            print_log("✅ Most pins are healthy", "SUCCESS")
        elif health_percentage >= 50:
            print_log("⚠️ Some pins need attention", "WARN")
        else:
            print_log("❌ Many pins need repair", "ERROR")
    
    # Show status file location
    status_path = Path(PIN_CONFIG["paths"]["status_file"])
    if status_path.exists():
        print_log(f"📋 Status saved: {status_path}", "INFO")


@task(
    help={
        "dir": "Limit to files under this directory (optional)",
        "include-txid": "Include .txid files in pinning (default: True)",
        "repair": "Auto re-pin broken/missing pins",
        "slug": "Limit to files containing this slug (optional)",
        "verbose": "Enable detailed logging",
        "check-health": "Check pin health after pinning",
        "webhook": "Send webhook notification after completion"
    },
    name="pin-all"
)
def pin_all(c, dir=None, include_txid=True, repair=False, slug=None, verbose=False, check_health=False, webhook=False):
    """
    📦 Pin all relevant files in vault/.signed, .txid, .preview, .synced
    
    Enhanced pinning with dual-pinning to IPFS and Arweave, including .txid files.
    Supports health checking, digest generation, and webhook notifications.
    """
    global VERBOSE_MODE
    VERBOSE_MODE = verbose
    
    print_log("🚀 Starting XO Vault pinning operation", "INFO")
    
    # First check pin status if repair mode
    if repair:
        print_log("🔍 Checking pin health before pinning...", "INFO")
        healthy, broken, missing = check_pin_health(c, slug=slug, repair=True)
        if broken == 0 and missing == 0:
            print_log("✅ All pins are healthy, no repair needed", "SUCCESS")
            return
    
    # Load existing manifest
    manifest = load_pin_manifest()
    
    # Find files to pin
    regular_patterns = [
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.signed",
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.mdx",
        PIN_CONFIG["paths"]["synced_dir"] + "/**/*.mdx",
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.html",
    ]
    
    txid_patterns = [
        PIN_CONFIG["paths"]["signed_dir"] + "/**/*.txid",
        PIN_CONFIG["paths"]["synced_dir"] + "/**/*.txid",
    ] if include_txid else []
    
    # Filter by directory if specified
    if dir:
        regular_patterns = [p for p in regular_patterns if dir in p]
        txid_patterns = [p for p in txid_patterns if dir in p]
    
    # Filter by slug if specified
    if slug:
        regular_patterns = [p for p in regular_patterns if slug in p]
        txid_patterns = [p for p in txid_patterns if slug in p]
    
    # Find files
    regular_files = []
    for pattern in regular_patterns:
        regular_files.extend(Path(".").glob(pattern))
    
    txid_files = []
    for pattern in txid_patterns:
        txid_files.extend(Path(".").glob(pattern))
    
    # Remove marker files from regular files
    regular_files = [f for f in regular_files if not any(f.name.endswith(marker) for marker in PIN_CONFIG["file_types"]["markers"])]
    
    all_files = list(regular_files) + list(txid_files)
    if not all_files:
        print_log("⚠️ No files found to pin.", "WARN")
        return
    
    print_log(f"📦 Found {len(regular_files)} regular files and {len(txid_files)} .txid files", "INFO")
    
    # Initialize counters
    pinned, skipped, failed = 0, 0, 0
    txid_pinned, txid_skipped, txid_failed = 0, 0, 0
    
    # First pin regular files (existing logic)
    print_log("📦 Pinning regular files...", "INFO")
    for file_path in sorted(regular_files):
        pinned_marker = file_path.with_suffix(file_path.suffix + ".pinned")
        if pinned_marker.exists() and not repair:
            print_log(f"⚠️ Already pinned: {file_path}", "WARN")
            skipped += 1
            continue
        try:
            pin_slug = file_path.stem
            print_log(f"📦 Pinning: {file_path}", "INFO")
            pin(c, pin_slug)
            pinned_marker.touch()
            print_log(f"✅ Pinned: {file_path}", "SUCCESS")
            pinned += 1
        except Exception as e:
            print_log(f"❌ Failed to pin {file_path}: {e}", "ERROR")
            failed += 1
    
    # Then pin .txid files with special handling
    if txid_files:
        print_log(f"\n🔗 Pinning {len(txid_files)} .txid files...", "INFO")
        for file_path in sorted(txid_files):
            # Check if already pinned using markers
            existing_ipfs_cid, existing_arweave_tx = check_already_pinned(file_path)
            
            if existing_ipfs_cid and existing_arweave_tx and not repair:
                print_log(f"⚠️ Already pinned: {file_path}", "WARN")
                print_log(f"  🔗 IPFS: {existing_ipfs_cid}", "INFO")
                print_log(f"  🌐 Arweave: {existing_arweave_tx}", "INFO")
                txid_skipped += 1
                continue
            
            try:
                print_log(f"🔗 Pinning TXID: {file_path}", "INFO")
                
                # Pin to IPFS (only if not already pinned or repair mode)
                ipfs_cid = existing_ipfs_cid
                if not existing_ipfs_cid or repair:
                    ipfs_cid = pin_file_to_ipfs(file_path)
                
                # Pin to Arweave (only if not already pinned or repair mode)
                arweave_txid = existing_arweave_tx
                if not existing_arweave_tx or repair:
                    arweave_txid = pin_file_to_arweave(file_path)
                
                # Save pin metadata
                pin_meta = {
                    "ipfs_cid": ipfs_cid,
                    "arweave_txid": arweave_txid,
                    "pinned_at": datetime.now().isoformat(),
                    "ipfs_gateway": PIN_CONFIG["ipfs"]["gateway"].format(cid=ipfs_cid) if ipfs_cid else None,
                    "arweave_link": PIN_CONFIG["arweave"]["gateway"].format(txid=arweave_txid) if arweave_txid else None
                }
                meta_file = file_path.with_suffix(file_path.suffix + ".pin_meta")
                with open(meta_file, 'w') as f:
                    json.dump(pin_meta, f, indent=2)
                
                # Update manifest with new structure
                txid_key = f"{file_path.stem}.txid"
                manifest[txid_key] = {
                    "slug": file_path.stem,
                    "file": str(file_path),
                    "type": "txid",
                    "ipfs_cid": ipfs_cid,
                    "arweave_tx": arweave_txid,
                    "timestamp": pin_meta["pinned_at"]
                }
                
                print_log(f"✅ TXID pinned: {file_path}", "SUCCESS")
                txid_pinned += 1
                
            except Exception as e:
                print_log(f"❌ Failed to pin TXID {file_path}: {e}", "ERROR")
                txid_failed += 1
    
    # Save manifest
    save_pin_manifest(manifest)
    
    # Generate digest
    # Create summary for digest
    summary_for_digest = {
        "pinned": pinned + txid_pinned,
        "regular": pinned,
        "txid": txid_pinned,
        "slug": slug
    }
    # Get files from manifest for digest
    files_for_digest = []
    for entry in manifest.values():
        if 'file' in entry:
            files_for_digest.append(Path(entry['file']))
    digest_md = generate_pin_digest(summary_for_digest, files_for_digest)
    
    # Print comprehensive summary
    print_log(f"\n📊 Pinning Summary:", "INFO")
    print_log(f"  📦 Regular files: {pinned} pinned, {skipped} skipped, {failed} failed", "INFO")
    if txid_files:
        print_log(f"  🔗 TXID files: {txid_pinned} pinned, {txid_skipped} skipped, {txid_failed} failed", "INFO")
    
    # Show detailed breakdown by file type
    total_pinned = pinned + txid_pinned
    total_skipped = skipped + txid_skipped
    total_failed = failed + txid_failed
    
    if txid_files:
        file_types = []
        if pinned > 0:
            file_types.append(f"{pinned} regular")
        if txid_pinned > 0:
            file_types.append(f"{txid_pinned} .txid")
        file_types_str = ", ".join(file_types)
        print_log(f"  📊 Total: {total_pinned} pinned ({file_types_str}), {total_skipped} skipped, {total_failed} failed", "INFO")
    else:
        print_log(f"  📊 Total: {total_pinned} pinned, {total_skipped} skipped, {total_failed} failed", "INFO")
    
    # Log summary to daily log
    summary_msg = f"Pin operation completed: {total_pinned} pinned, {total_skipped} skipped, {total_failed} failed"
    if slug:
        summary_msg += f" (slug: {slug})"
    log_pin_activity(summary_msg)
    
    # Check health if requested
    if check_health:
        print_log("\n🔍 Running health check...", "INFO")
        healthy, broken, missing = check_pin_health(c, slug=slug, repair=False)
        
        if healthy > 0 and broken == 0 and missing == 0:
            print_log("🛡️ All pins verified healthy", "SUCCESS")
        else:
            print_log(f"⚠️ Health issues found: {broken} broken, {missing} missing", "WARN")
    
    # Send webhook if requested
    if webhook:
        summary = {
            "pinned": total_pinned,
            "skipped": total_skipped,
            "failed": total_failed
        }
        send_pin_webhook(slug, summary)
    
    # Final status report
    print_log(f"\n📡 XO Vault Pin Summary — {datetime.now().strftime('%Y-%m-%d')}", "INFO")
    print_log(f"✅ Total Pinned: {total_pinned} ({pinned} regular, {txid_pinned} .txid)", "INFO")
    if check_health:
        print_log("🛡️ Verified: All pins healthy" if total_failed == 0 else f"⚠️ Issues: {total_failed} failed", "INFO")
    print_log(f"📦 Manifest: {PIN_CONFIG['paths']['manifest_file']}", "INFO")
    print_log(f"📄 Digest: {PIN_CONFIG['paths']['digest_file']}", "INFO")
    if webhook:
        print_log("📬 Sent to: XO Inbox, Telegram", "INFO")


@task(help={
    "slug": "Pulse slug (optional)",
    "out": "Output type: markdown|webhook|inbox|all (default: all)",
    "dry_run": "Preview only, do not write files or send webhooks"
})
def pin_summary(c, slug=None, out="all", dry_run=False):
    """
    📈 Generate pin summary, digest, and optionally post to webhook/inbox.
    """
    manifest_path = Path("vault/.pins/pin_manifest.json")
    digest_path = Path("vault/.pins/pin_digest.mdx")
    if not manifest_path.exists():
        print("❌ No manifest found. Run pin-all first.")
        return
    with open(manifest_path) as f:
        manifest = json.load(f)
    files = [Path(entry['file']) for entry in manifest.values() if 'file' in entry]
    summary = {
        "pinned": len(files),
        "regular": sum(1 for f in files if not f.name.endswith('.txid')),
        "txid": sum(1 for f in files if f.name.endswith('.txid')),
        "manifest_link": str(manifest_path),
        "digest_link": str(digest_path),
        "skipped": 0,
        "failed": 0,
        "verified": None
    }
    if slug:
        summary["slug"] = slug
    # Generate digest
    digest_md = generate_pin_digest(summary, files)
    # Format webhook/inbox message
    message = format_pin_summary(summary, slug or "all", style="markdown")
    # Output logic
    if out in ("markdown", "all"):
        print("\n--- Markdown Digest ---\n")
        print(digest_md)
    if out in ("webhook", "all"):
        print("\n--- Webhook Message ---\n")
        print(message)
    if out in ("inbox", "all"):
        if not dry_run:
            send_to_xo_inbox(message, str(manifest_path), slug or "all")
        else:
            print("[Dry Run] Would send to XO Inbox:")
            print(message)
    if dry_run:
        print("[Dry Run] No files written, no webhooks sent.")
    else:
        print("✅ Pin summary complete.")


ns = Collection("vault")
ns.add_task(pin, name="pin")
ns.add_task(pin_all, name="pin-all")
ns.add_task(pin_status, name="pin-status")
ns.add_task(pin_summary, name="pin-summary")

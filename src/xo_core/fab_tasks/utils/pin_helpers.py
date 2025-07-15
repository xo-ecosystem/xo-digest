"""
XO Vault Pin Helpers - Utility functions for pinning operations
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from invoke import task, Collection


@task
def pin_file_to_ipfs(file_path: Path, nft_storage_token: Optional[str] = None) -> Optional[str]:
    """Pin a single file to IPFS using nft.storage"""
    if not nft_storage_token:
        nft_storage_token = os.getenv("NFT_STORAGE_TOKEN")
    
    if not nft_storage_token:
        print("❌ NFT_STORAGE_TOKEN not set")
        return None
    
    headers = {
        "Authorization": f"Bearer {nft_storage_token}",
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(
                "https://api.nft.storage/upload", 
                headers=headers, 
                files=files
            )
        
        if response.status_code == 200:
            cid = response.json()["value"]["cid"]
            print(f"🔗 File pinned to IPFS: ipfs://{cid}")
            return cid
        else:
            print(f"❌ IPFS upload failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ IPFS pinning error: {e}")
        return None


def pin_file_to_arweave(file_path: Path) -> Optional[str]:
    """Pin a single file to Arweave using arweave-python-client"""
    try:
        # Try to use the existing arweave script
        result = subprocess.run(
            ["python", "scripts/pin_to_arweave.py", "--file", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Extract TXID from output
            for line in result.stdout.split('\n'):
                if 'TX ID:' in line:
                    txid = line.split('TX ID:')[-1].strip()
                    print(f"🔗 File pinned to Arweave: {txid}")
                    return txid
            print("✅ Arweave upload successful (TXID not found in output)")
            return "uploaded"
        else:
            print(f"❌ Arweave upload failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ Arweave upload timed out")
        return None
    except FileNotFoundError:
        print("⚠️ Arweave script not found, skipping Arweave pinning")
        return None
    except Exception as e:
        print(f"❌ Arweave pinning error: {e}")
        return None


def save_pin_metadata(file_path: Path, ipfs_cid: Optional[str], arweave_txid: Optional[str]) -> None:
    """Save pin metadata to file"""
    pin_meta = {
        "ipfs_cid": ipfs_cid,
        "arweave_txid": arweave_txid,
        "pinned_at": datetime.now().isoformat(),
        "ipfs_gateway": f"https://{ipfs_cid}.ipfs.nftstorage.link/" if ipfs_cid else None,
        "arweave_link": f"https://arweave.net/{arweave_txid}" if arweave_txid else None
    }
    
    meta_file = file_path.with_suffix(file_path.suffix + ".pin_meta")
    try:
        with open(meta_file, 'w') as f:
            json.dump(pin_meta, f, indent=2)
        print(f"📝 Pin metadata saved: {meta_file}")
    except Exception as e:
        print(f"❌ Error saving pin metadata: {e}")


def check_already_pinned(file_path: Path) -> tuple[Optional[str], Optional[str]]:
    """Check if file is already pinned using .ipfs_cid or .arweave_tx markers"""
    ipfs_marker = file_path.with_suffix(file_path.suffix + ".ipfs_cid")
    arweave_marker = file_path.with_suffix(file_path.suffix + ".arweave_tx")
    
    ipfs_cid = None
    arweave_tx = None
    
    if ipfs_marker.exists():
        try:
            ipfs_cid = ipfs_marker.read_text().strip()
        except:
            pass
    
    if arweave_marker.exists():
        try:
            arweave_tx = arweave_marker.read_text().strip()
        except:
            pass
    
    return ipfs_cid, arweave_tx


def validate_cid(cid: str) -> bool:
    """Validate IPFS CID format"""
    return cid.startswith('bafy') if cid else False


def test_gateway_accessibility(gateway_url: str, timeout: int = 10) -> bool:
    """Test if gateway URL is accessible"""
    try:
        response = requests.head(gateway_url, timeout=timeout)
        return response.status_code == 200
    except:
        return False 


ns = Collection("utils-pin-helpers")
ns.add_task(pin_file_to_ipfs)

from invoke import Collection

ns = Collection()

"""
from xo_core.vault.ipfs_utils import pin_to_ipfs
IPFS Utilities for XO Vault

This module provides robust IPFS pinning functionality with support for multiple backends:
- Pinata (via JWT)
- nft.storage (via API token)
- Local IPFS daemon (fallback)

Designed for Codex/Agent0 assistance and easy testing.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Union
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()




class IPFSBackendError(Exception):
    """Raised when IPFS backend operations fail."""
    pass

def pin_to_ipfs(file_path: Union[str, Path], provider: Optional[str] = None) -> str:
    """
    Pin a file to IPFS using the specified or configured backend.
    
    Args:
        file_path: Path to the file to pin
        provider: Override the IPFS_PROVIDER environment variable
        
    Returns:
        IPFS URI (ipfs://<cid>)
        
    Raises:
        IPFSBackendError: If pinning fails
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> pin_to_ipfs("vault/signed/pulse.mdx")
        'ipfs://QmFakeCID123...'
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine provider
    provider = provider or os.getenv("IPFS_PROVIDER", "nftstorage").lower()
    
    log_status(f"📦 Pinning {file_path} to IPFS using {provider}", level="info")
    
    try:
        if provider == "pinata":
            return _pin_to_pinata(file_path)
        elif provider == "nftstorage":
            return _pin_to_nftstorage(file_path)
        elif provider == "local":
            return _pin_to_local(file_path)
        else:
            raise IPFSBackendError(f"Unsupported IPFS provider: {provider}")
    except Exception as e:
        log_status(f"❌ Failed to pin {file_path} to {provider}: {e}", level="error")
        raise IPFSBackendError(f"IPFS pinning failed: {e}")

def _pin_to_pinata(file_path: Path) -> str:
    """Pin file to Pinata IPFS service."""
    api_key = os.getenv("PINATA_API_KEY")
    if not api_key:
        raise IPFSBackendError("PINATA_API_KEY not configured")
    
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/octet-stream"
    }
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "application/octet-stream")}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code != 200:
        raise IPFSBackendError(f"Pinata API error: {response.status_code} - {response.text}")
    
    result = response.json()
    cid = result.get("IpfsHash")
    if not cid:
        raise IPFSBackendError("No CID returned from Pinata")
    
    log_status(f"✅ Pinned to Pinata: {cid}", level="success")
    return f"ipfs://{cid}"

def _pin_to_nftstorage(file_path: Path) -> str:
    """Pin file to nft.storage IPFS service."""
    api_token = os.getenv("NFT_STORAGE_TOKEN")
    if not api_token:
        raise IPFSBackendError("NFT_STORAGE_TOKEN not configured")
    
    url = "https://api.nft.storage/upload"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/octet-stream"
    }
    
    with open(file_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f)
    
    if response.status_code != 200:
        raise IPFSBackendError(f"nft.storage API error: {response.status_code} - {response.text}")
    
    result = response.json()
    cid = result.get("value", {}).get("cid")
    if not cid:
        raise IPFSBackendError("No CID returned from nft.storage")
    
    log_status(f"✅ Pinned to nft.storage: {cid}", level="success")
    return f"ipfs://{cid}"

def _pin_to_local(file_path: Path) -> str:
    """Pin file to local IPFS daemon."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["ipfs", "add", "-Q", str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        cid = result.stdout.strip()
        log_status(f"✅ Pinned to local IPFS: {cid}", level="success")
        return f"ipfs://{cid}"
    except subprocess.CalledProcessError as e:
        raise IPFSBackendError(f"Local IPFS error: {e.stderr}")
    except FileNotFoundError:
        raise IPFSBackendError("IPFS CLI not found. Install with: brew install ipfs")

def get_ipfs_gateway_url(cid: str, gateway: str = "nftstorage") -> str:
    """
    Get HTTP gateway URL for an IPFS CID.
    
    Args:
        cid: IPFS content identifier
        gateway: Gateway provider (nftstorage, ipfs.io, cloudflare)
        
    Returns:
        HTTP URL to access the content
    """
    gateways = {
        "nftstorage": f"https://{cid}.ipfs.nftstorage.link/",
        "ipfs.io": f"https://ipfs.io/ipfs/{cid}",
        "cloudflare": f"https://cloudflare-ipfs.com/ipfs/{cid}"
    }
    
    return gateways.get(gateway, gateways["nftstorage"])

# Codex-friendly function for testing
def test_ipfs_connection(provider: Optional[str] = None) -> Dict[str, str]:
    """
    Test IPFS backend connectivity and configuration.
    
    Returns:
        Dict with test results and status
    """
    provider = provider or os.getenv("IPFS_PROVIDER", "nftstorage")
    
    results = {
        "provider": provider,
        "status": "unknown",
        "message": "",
        "config": {}
    }
    
    try:
        if provider == "pinata":
            api_key = os.getenv("PINATA_API_KEY")
            results["config"]["api_key"] = "configured" if api_key else "missing"
        elif provider == "nftstorage":
            api_token = os.getenv("NFT_STORAGE_TOKEN")
            results["config"]["api_token"] = "configured" if api_token else "missing"
        elif provider == "local":
            import subprocess
            subprocess.run(["ipfs", "--version"], capture_output=True, check=True)
            results["config"]["ipfs_cli"] = "available"
        
        results["status"] = "ready"
        results["message"] = f"IPFS {provider} backend is configured and ready"
        
    except Exception as e:
        results["status"] = "error"
        results["message"] = str(e)
    
    return results

from rich.console import Console
from rich.markup import escape

console = Console()

def log_status(message, level="info"):
    if level == "success":
        console.print(f"[bold green]{escape(message)}[/bold green]")
    elif level == "error":
        console.print(f"[bold red]{escape(message)}[/bold red]")
    else:
        console.print(f"[dim]{escape(message)}[/dim]")
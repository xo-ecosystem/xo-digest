"""
IPFS Fabric Tasks for XO Core

Provides tasks for testing IPFS connectivity, pinning files, and managing IPFS operations.
"""

from invoke import task, Collection
from pathlib import Path
import os

from xo_core.vault.ipfs_utils import (
    pin_to_ipfs, 
    test_ipfs_connection, 
    get_ipfs_gateway_url,
    IPFSBackendError
)

@task
def test_connection(c, provider=None):
    """
    Test IPFS backend connectivity and configuration.
    
    Args:
        provider: Override IPFS_PROVIDER environment variable
    """
    print("🔍 Testing IPFS connection...")
    result = test_ipfs_connection(provider)
    
    print(f"Provider: {result['provider']}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Config: {result['config']}")
    
    if result['status'] == 'ready':
        print("✅ IPFS backend is ready!")
    else:
        print("❌ IPFS backend has issues")

@task
def pin_file(c, file_path, provider=None):
    """
    Pin a file to IPFS.
    
    Args:
        file_path: Path to the file to pin
        provider: Override IPFS_PROVIDER environment variable
    """
    try:
        print(f"📦 Pinning {file_path} to IPFS...")
        cid = pin_to_ipfs(file_path, provider)
        print(f"✅ Successfully pinned: {cid}")
        
        # Show gateway URLs
        cid_only = cid.replace("ipfs://", "")
        print(f"🌐 Gateway URLs:")
        print(f"  nft.storage: {get_ipfs_gateway_url(cid_only, 'nftstorage')}")
        print(f"  ipfs.io: {get_ipfs_gateway_url(cid_only, 'ipfs.io')}")
        print(f"  Cloudflare: {get_ipfs_gateway_url(cid_only, 'cloudflare')}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except IPFSBackendError as e:
        print(f"❌ IPFS error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

@task
def test_all(c):
    """Run all IPFS tests and checks."""
    print("🧪 Running comprehensive IPFS tests...")
    
    # Test connection
    print("\n1. Testing IPFS connection...")
    result = test_ipfs_connection()
    if result['status'] != 'ready':
        print("❌ IPFS connection test failed")
        return
    
    # Test with a sample file
    print("\n2. Testing file pinning...")
    test_file = Path("test_ipfs_sample.txt")
    try:
        with open(test_file, "w") as f:
            f.write("Hello from XO Core IPFS test!")
        
        cid = pin_to_ipfs(test_file)
        print(f"✅ Test file pinned: {cid}")
        
        # Clean up
        test_file.unlink()
        
    except Exception as e:
        print(f"❌ File pinning test failed: {e}")
        if test_file.exists():
            test_file.unlink()
    
    print("\n✅ All IPFS tests completed!")

@task
def list_providers(c):
    """List available IPFS providers and their configuration status."""
    providers = ["nftstorage", "pinata", "local"]
    
    print("📋 Available IPFS Providers:")
    print("=" * 50)
    
    for provider in providers:
        print(f"\n🔧 {provider.upper()}:")
        result = test_ipfs_connection(provider)
        
        if result['status'] == 'ready':
            print(f"  ✅ Status: Ready")
            if result['config']:
                for key, value in result['config'].items():
                    print(f"  📝 {key}: {value}")
        else:
            print(f"  ❌ Status: {result['status']}")
            print(f"  💬 Message: {result['message']}")

@task
def setup_env(c):
    """Interactive setup for IPFS environment variables."""
    print("🔧 IPFS Environment Setup")
    print("=" * 30)
    
    print("\nChoose your IPFS provider:")
    print("1. nft.storage (recommended)")
    print("2. Pinata")
    print("3. Local IPFS daemon")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    provider_map = {
        "1": "nftstorage",
        "2": "pinata", 
        "3": "local"
    }
    
    provider = provider_map.get(choice, "nftstorage")
    
    print(f"\nSelected provider: {provider}")
    
    if provider == "nftstorage":
        token = input("Enter your nft.storage API token: ").strip()
        if token:
            print(f"Add to your .env file:")
            print(f"IPFS_PROVIDER=nftstorage")
            print(f"NFT_STORAGE_TOKEN={token}")
    
    elif provider == "pinata":
        token = input("Enter your Pinata JWT token: ").strip()
        if token:
            print(f"Add to your .env file:")
            print(f"IPFS_PROVIDER=pinata")
            print(f"PINATA_API_KEY={token}")
    
    elif provider == "local":
        print("Make sure IPFS CLI is installed:")
        print("brew install ipfs")
        print("\nAdd to your .env file:")
        print(f"IPFS_PROVIDER=local")

# Create namespace
ns = Collection("ipfs")
ns.add_task(test_connection, name="test-connection")
ns.add_task(pin_file, name="pin-file")
ns.add_task(test_all, name="test-all")
ns.add_task(list_providers, name="list-providers")
ns.add_task(setup_env, name="setup-env") 
import requests
import sys
import os

PINATA_JWT = os.getenv("PINATA_JWT")

print("🔁 Running latest Pinata-only version of ipfs_pin.py")
print("DEBUG PINATA_JWT:", PINATA_JWT[:20] if PINATA_JWT else "NOT SET")

def pin_file_to_ipfs(filepath):
    if PINATA_JWT:
        with open(filepath, "rb") as f:
            response = requests.post(
                "https://api.pinata.cloud/pinning/pinFileToIPFS",
                headers={"Authorization": f"Bearer {PINATA_JWT}"},
                files={"file": ("file", f.read())},
            )
        source = "Pinata"
    else:
        print("❌ No supported IPFS pinning credentials set (PINATA_JWT required).")
        return

    if response.ok:
        cid = response.json().get("IpfsHash", "unknown")
        print(f"📦 File pinned via {source}: ipfs://{cid}/{os.path.basename(filepath)}")
    else:
        print(f"❌ {source} upload failed: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ipfs_pin.py <path/to/file>")
    else:
        pin_file_to_ipfs(sys.argv[1])
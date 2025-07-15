import os
import requests
import json
from typing import Dict, List

# Environment keys
INFURA_URL = os.getenv("INFURA_API_URL", "https://ipfs.infura.io:5001/api/v0/add")
NFT_STORAGE_API = os.getenv("NFT_STORAGE_API")
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET")

def upload_to_infura(file_path: str) -> Dict:
    with open(file_path, "rb") as f:
        response = requests.post(INFURA_URL, files={"file": f})
    response.raise_for_status()
    result = response.json()
    return {
        "service": "infura",
        "hash": result["Hash"],
        "url": f"https://ipfs.io/ipfs/{result['Hash']}"
    }

def upload_to_nft_storage(file_path: str) -> Dict:
    if not NFT_STORAGE_API:
        return {"service": "nft.storage", "error": "API key not configured"}
    with open(file_path, "rb") as f:
        headers = {"Authorization": f"Bearer {NFT_STORAGE_API}"}
        response = requests.post("https://api.nft.storage/upload", headers=headers, files={"file": f})
    response.raise_for_status()
    cid = response.json()["value"]["cid"]
    return {
        "service": "nft.storage",
        "hash": cid,
        "url": f"https://nftstorage.link/ipfs/{cid}"
    }

def upload_to_pinata(file_path: str) -> Dict:
    if not PINATA_API_KEY or not PINATA_API_SECRET:
        return {"service": "pinata", "error": "API keys not configured"}
    with open(file_path, "rb") as f:
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_API_SECRET
        }
        response = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", headers=headers, files={"file": f})
    response.raise_for_status()
    ipfs_hash = response.json()["IpfsHash"]
    return {
        "service": "pinata",
        "hash": ipfs_hash,
        "url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    }

def upload_to_arweave(file_path: str) -> Dict:
    try:
        import arweave
        wallet_path = os.getenv("ARWEAVE_WALLET_PATH", "arweave.json")
        wallet = arweave.Wallet(wallet_path)
        transaction = arweave.Transaction(wallet, data_path=file_path)
        transaction.sign()
        transaction.send()
        return {
            "service": "arweave",
            "id": transaction.id,
            "url": f"https://arweave.net/{transaction.id}"
        }
    except Exception as e:
        return {"service": "arweave", "error": str(e)}

def upload_file(file_path: str) -> List[Dict]:
    results = []
    try:
        results.append(upload_to_infura(file_path))
    except Exception as e:
        results.append({"service": "infura", "error": str(e)})
    try:
        results.append(upload_to_nft_storage(file_path))
    except Exception as e:
        results.append({"service": "nft.storage", "error": str(e)})
    try:
        results.append(upload_to_pinata(file_path))
    except Exception as e:
        results.append({"service": "pinata", "error": str(e)})
    try:
        results.append(upload_to_arweave(file_path))
    except Exception as e:
        results.append({"service": "arweave", "error": str(e)})
    return results


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload a file to multiple IPFS/Arweave services")
    parser.add_argument("file", help="Path to the file to upload")
    args = parser.parse_args()

    result = upload_file(args.file)
    print(json.dumps(result, indent=2))


# Alias for backward compatibility
upload_to_ipfs = upload_file  # Alias for backward compatibility
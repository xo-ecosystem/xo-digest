import argparse
import requests
from pathlib import Path

def upload_to_nft_storage(file_path: Path, api_token: str):
    url = "https://api.nft.storage/upload"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/octet-stream",
    }

    with file_path.open("rb") as file_data:
        response = requests.post(url, headers=headers, data=file_data)

    if response.status_code == 200:
        cid = response.json()["value"]["cid"]
        print(f"✅ Uploaded to IPFS via nft.storage. CID: {cid}")
    else:
        print(f"❌ Upload to nft.storage failed: {response.status_code} – {response.text}")

def upload_to_lighthouse(file_path: Path, api_token: str):
    url = "https://node.lighthouse.storage/api/v0/add"
    headers = {
        "Authorization": api_token
    }

    with file_path.open("rb") as file_data:
        files = {'file': file_data}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        cid = response.json()["Hash"]
        print(f"✅ Uploaded to IPFS via Lighthouse. CID: {cid}")
    else:
        print(f"❌ Upload to Lighthouse failed: {response.status_code} – {response.text}")

def upload_to_thirdweb(file_path: Path, api_token: str):
    from thirdweb import ThirdwebStorage

    storage = ThirdwebStorage(api_token)
    try:
        uri = storage.upload(str(file_path))
        print(f"✅ Uploaded to IPFS via Thirdweb. URI: {uri}")
    except Exception as e:
        print(f"❌ Upload to Thirdweb failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload a file to decentralized storage using nft.storage, lighthouse.storage, or Thirdweb."
    )
    parser.add_argument("--file", required=True, help="Path to the file to upload")
    parser.add_argument("--token", required=True, help="API token for the selected storage provider")
    parser.add_argument(
        "--provider",
        choices=["nft", "lighthouse", "thirdweb"],
        default="nft",
        help="Storage provider to use: nft, lighthouse, or thirdweb"
    )

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print("❌ File does not exist:", file_path)
    else:
        if args.provider == "nft":
            upload_to_nft_storage(file_path, args.token)
        elif args.provider == "lighthouse":
            upload_to_lighthouse(file_path, args.token)
        elif args.provider == "thirdweb":
            upload_to_thirdweb(file_path, args.token)


import argparse
import json
import os
import requests

THIRDWEB_UPLOAD_URL = "https://upload.thirdweb.com"

def upload_file_to_thirdweb(file_path, api_key=None):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "rb") as f:
        files = {"file": f}
        headers = {}
        if api_key:
            headers["x-secret-key"] = api_key

        response = requests.post(THIRDWEB_UPLOAD_URL, files=files, headers=headers)
        response.raise_for_status()

        result = response.json()
        uri = result.get("uri") or result.get("IpfsHash")
        if not uri:
            raise Exception("Upload failed: No URI returned.")

        return uri

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a file to Thirdweb IPFS")
    parser.add_argument("file_path", help="Path to the file to upload")
    parser.add_argument("--api-key", help="Optional Thirdweb API key")

    args = parser.parse_args()
    try:
        ipfs_uri = upload_file_to_thirdweb(args.file_path, api_key=args.api_key)
        print(f"✅ Uploaded to Thirdweb IPFS: {ipfs_uri}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
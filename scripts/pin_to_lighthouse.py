

import os
import sys
import requests
from pathlib import Path

LIGHTHOUSE_API_URL = "https://node.lighthouse.storage/api/v0/add"
LIGHTHOUSE_API_TOKEN = os.getenv("LIGHTHOUSE_API_TOKEN")

def pin_file_to_lighthouse(file_path):
    if not LIGHTHOUSE_API_TOKEN:
        print("❌ LIGHTHOUSE_API_TOKEN is not set.")
        return None

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return None

    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {LIGHTHOUSE_API_TOKEN}'}
        response = requests.post(LIGHTHOUSE_API_URL, headers=headers, files=files)

    if response.status_code == 200:
        cid = response.json().get("Hash")
        print(f"✅ File pinned to Lighthouse. CID: {cid}")
        return cid
    else:
        print(f"❌ Failed to pin file. Status: {response.status_code}, Response: {response.text}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/pin_to_lighthouse.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    pin_file_to_lighthouse(file_path)
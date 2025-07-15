

import os
import json
from pathlib import Path
from arweave.arweave_lib import Wallet, Transaction

def load_wallet(wallet_path):
    if not os.path.exists(wallet_path):
        raise FileNotFoundError(f"Arweave wallet not found at {wallet_path}")
    return Wallet(wallet_path)

def pin_file_to_arweave(wallet, file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found")
    with file_path.open("rb") as f:
        tx = Transaction(wallet, f.read())
        tx.add_tag("Content-Type", "text/plain")
        tx.sign()
        tx.send()
    return tx.id

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pin a file to Arweave")
    parser.add_argument("--wallet", type=str, default="secrets/.arweave.key.json", help="Path to Arweave wallet")
    parser.add_argument("--file", type=str, required=True, help="Path to the file to pin")
    args = parser.parse_args()

    wallet = load_wallet(args.wallet)
    tx_id = pin_file_to_arweave(wallet, args.file)
    print(f"✅ Pinned {args.file} to Arweave with TX ID: {tx_id}")
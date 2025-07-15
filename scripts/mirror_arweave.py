

import os
import json
import arweave

def mirror_to_arweave(file_path, wallet_path=None):
    wallet_path = wallet_path or os.getenv("ARWEAVE_WALLET_JSON", "secrets/arweave_wallet.json")
    if not os.path.exists(wallet_path):
        raise FileNotFoundError(f"Arweave wallet not found: {wallet_path}")
    
    with open(wallet_path, 'r') as f:
        keyfile = json.load(f)

    wallet = arweave.Wallet(keyfile)
    tx = arweave.Transaction(wallet, file_path=file_path)
    tx.add_tag('App-Name', 'XO-Vault')
    tx.add_tag('Content-Type', 'application/octet-stream')
    tx.sign()
    tx.send()

    return {
        "status": "success",
        "arweave_tx_id": tx.id,
        "arweave_url": f"https://arweave.net/{tx.id}"
    }
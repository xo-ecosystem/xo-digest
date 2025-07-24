from invoke import task
from pathlib import Path
import subprocess
import os
from pathlib import Path

@task
def pull_secrets(c, enc_file='vault/.keys.enc', out_file='vault/unseal_keys.json'):
    if not Path(enc_file).exists():
        print(f"❌ Encrypted key file not found: {enc_file}")
        return False

    print(f"🔐 Decrypting {enc_file}...")
    try:
        subprocess.run(['gpg', '--output', out_file, '--decrypt', enc_file], check=True)
        print(f"✅ Decrypted keys saved to: {out_file}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to decrypt keys.")
        return False

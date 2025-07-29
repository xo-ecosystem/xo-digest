from invoke import task
from pathlib import Path
import subprocess
import os
from dotenv import load_dotenv

@task
def decrypt_keys(c, enc_file='vault/.keys.enc', out_file='vault/unseal_keys.json'):
    if not Path(enc_file).exists():
        print(f"❌ Encrypted key file not found: {enc_file}")
        return False

    print(f"🔐 Decrypting {enc_file}...")
    try:
        subprocess.run(['gpg', '--output', out_file, '--decrypt', enc_file], check=True)
        print(f"✅ Decrypted keys saved to: {out_file}")

        # Optional: Load resulting keys into environment if .envrc exists
        if Path(".envrc").exists():
            load_dotenv(".envrc")
            print("📥 .envrc loaded into environment")
            # Optional: Auto-unseal Vault if unseal keys are available
            unseal_keys = [os.getenv(f"VAULT_UNSEAL_KEY_{i}") for i in range(1, 4)]
            if all(unseal_keys):
                print("🔓 Attempting to unseal Vault...")
                for key in unseal_keys:
                    subprocess.run(["curl", "--request", "PUT", "--data", f'{{\"key\":\"{key}\"}}', f"{os.getenv('VAULT_ADDR')}/v1/sys/unseal"], check=True)
                print("✅ Vault unseal attempt completed")
            else:
                print("⚠️ Unseal keys missing in environment. Skipping auto-unseal.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to decrypt keys.")
        return False


# Chained Fabric task: pull → decrypt → unseal
from invoke import task

@task
def bootstrap(c):
    from .pull_secrets import pull_secrets
    print("🚀 Bootstrapping Vault: pull → decrypt → unseal")
    if pull_secrets(c):
        decrypt_keys(c)
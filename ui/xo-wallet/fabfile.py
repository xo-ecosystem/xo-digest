from fabric import task
import shutil
from pathlib import Path

@task
def deploy(c):
    """Deploy the XO Wallet UI to public/wallet/"""
    src = Path(__file__).resolve().parent
    dest = Path(__file__).resolve().parents[2] / "public" / "wallet"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    print(f"✅ XO Wallet UI deployed to: {dest}")

@task
def deploy_with_config(c):
    """Deploy the XO Wallet UI with config to public/wallet/"""
    src = Path(__file__).resolve().parent
    dest = Path(__file__).resolve().parents[2] / "public" / "wallet"
    deploy(c)
    config_file = src / "xo-wallet-config.json"
    shutil.copy(config_file, dest / "xo-wallet-config.json")
    print(f"✅ Config deployed to: {dest / 'xo-wallet-config.json'}")

from invoke import task
import subprocess
import os
import json
from invoke import Collection
ns = Collection("wallet")

@task
def deploy_with_config(c):
    """
    Deploy the custom XO wallet UI with a local config.
    """
    print("🚀 Deploying XO Wallet UI...")

    config_path = os.path.join(os.getcwd(), "xo-wallet-config.json")
    if not os.path.exists(config_path):
        print("❌ Config file not found at xo-wallet-config.json")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    print("🧾 Loaded config:")
    print(json.dumps(config, indent=2))

    # Optional: pass config values into env if needed
    env = os.environ.copy()
    env["XO_WALLET_THEME"] = config.get("theme", "default")
    env["XO_WALLET_NETWORK"] = config.get("network", "goerli")

    subprocess.run(["npm", "run", "build"], env=env)
    subprocess.run(["npm", "run", "deploy"], env=env)

    print("✅ Wallet UI deployed with custom config.")

ns.add_task(deploy_with_config, "deploy_with_config")
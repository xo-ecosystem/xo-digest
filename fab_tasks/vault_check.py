from invoke import task
import importlib.util
import sys
from pathlib import Path


@task
def vault_check(c):
    """🔍 Validate XO Vault unseal + bootstrap + agent dispatch"""

    base = Path(__file__).parent.parent / "src" / "xo_core"

    # --- Load utils.py (contains unseal and bootstrap) ---
    print("🔐 Checking XO Vault unseal and bootstrap from utils.py...")
    spec = importlib.util.spec_from_file_location("utils", base / "vault" / "utils.py")
    if spec and spec.loader:
        utils = importlib.util.module_from_spec(spec)
        sys.modules["utils"] = utils
        spec.loader.exec_module(utils)
    else:
        print("❌ Could not load utils module")
        return

    # Test unseal functionality
    print("\n🔐 Testing vault unseal...")
    try:
        utils.unseal_vault(c)
    except Exception as e:
        print(f"⚠️ Unseal test failed: {e}")

    # Test bootstrap functionality
    print("\n🔧 Testing vault bootstrap...")
    try:
        utils.run_bootstrap(c)
    except Exception as e:
        print(f"⚠️ Bootstrap test failed: {e}")

    # --- Agent Dispatch ---
    print("\n🧠 Checking agent.dispatch (vault_keeper)...")
    try:
        spec = importlib.util.spec_from_file_location(
            "agent_reply", base / "vault" / "agent_reply.py"
        )
        if spec and spec.loader:
            agent = importlib.util.module_from_spec(spec)
            sys.modules["agent_reply"] = agent
            spec.loader.exec_module(agent)

            agent.dispatch_persona(persona="vault_keeper", preview=True)
        else:
            print("❌ Could not load agent_reply module")
    except Exception as e:
        print(f"⚠️ Agent dispatch test failed: {e}")

    print("\n✅ XO Vault check completed")

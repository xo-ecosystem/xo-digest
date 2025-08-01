# src/xo_core/agent/plugins/ens_resolver.py
from web3 import Web3
from pathlib import Path
import yaml
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
web3 = Web3(HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))


def resolve_all_ens(names: list[str]) -> dict:
    resolved = {}
    for name in names:
        try:
            address = w3.ens.address(name)
            resolved[name] = {
                "address": address or None,
                "resolved": address is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            resolved[name] = {
                "error": str(e),
                "resolved": False,
            }
    return resolved


def update_handles_registry(resolved_dict: dict):
    registry_path = Path("vault/registry/handles.yml")
    if not registry_path.exists():
        print("⚠️ Registry file not found, creating new one...")
        data = {}
    else:
        data = yaml.safe_load(registry_path.read_text()) or {}

    for name, info in resolved_dict.items():
        handle = name.split(".")[0].replace("-", "")
        if name not in data:
            data[name] = {"handle": handle, "platforms": {}}
        data[name]["platforms"]["ens"] = info

    with open(registry_path, "w") as f:
        yaml.safe_dump(data, f)
    print(f"✅ Updated {registry_path} with ENS records")

from datetime import datetime

from xo_core.agent.plugins.dispatch import dispatch_persona


def run_handle_guardian(domain_list):
    # ... existing logic processing domain_list ...

    with open("vault/logbook/seal.log", "a") as log:
        log.write(f"[handle_guardian] {datetime.utcnow().isoformat()} - Scanned {len(domain_list)} domains\n")


def reserve_handles(domain_list):
    from pathlib import Path
    import json

    registry_path = Path("vault/registry/handles.yml")
    if not registry_path.exists():
        print("⚠️ Registry file not found.")
        return

    reserved_path = Path("vault/registry/reserved.json")
    reserved = {}

    for domain in domain_list:
        handle = domain.split(".")[0].replace("-", "")
        reserved[domain] = {
            "handle": handle,
            "reserved": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    reserved_path.parent.mkdir(parents=True, exist_ok=True)
    with open(reserved_path, "w") as f:
        json.dump(reserved, f, indent=2)
    print(f"✅ Reserved handles saved to {reserved_path}")
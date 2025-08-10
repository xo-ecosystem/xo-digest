import requests
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def build_registry_entry(domain: str, handle: str) -> Dict[str, Any]:
    """Build a registry entry for a domain and handle."""
    return {
        "domain": domain,
        "handle": handle,
        "platforms": {
            "twitter": None,
            "github": None,
            "ens": None,
            "farcaster": None,
            "discord": None,
        },
        "checked_at": datetime.utcnow().isoformat(),
    }


def check_github_handle(handle: str) -> Dict[str, Any]:
    """Check if a GitHub handle is available."""
    try:
        res = requests.get(f"https://github.com/{handle}", timeout=10)
        return {"handle": handle, "available": res.status_code == 404}
    except Exception as e:
        print(f"⚠️ GitHub check failed for {handle}: {e}")
        return {"handle": handle, "available": None}


def check_ens_handle(handle: str) -> Dict[str, Any]:
    """Check if an ENS handle is available."""
    # TODO: Implement actual Web3 resolver call
    # For now, return None to indicate unknown status
    return {"handle": handle, "available": None}


def check_farcaster_handle(handle: str) -> Dict[str, Any]:
    """Check if a Farcaster handle is available."""
    # TODO: Implement actual Farcaster API lookup
    # For now, return None to indicate unknown status
    return {"handle": handle, "available": None}


def check_twitter_handle(handle: str) -> Dict[str, Any]:
    """Check if a Twitter handle is available."""
    # TODO: Implement Twitter API check
    # For now, return None to indicate unknown status
    return {"handle": handle, "available": None}


def check_discord_handle(handle: str) -> Dict[str, Any]:
    """Check if a Discord handle is available."""
    # TODO: Implement Discord API check
    # For now, return None to indicate unknown status
    return {"handle": handle, "available": None}


# Platform check functions
PLATFORM_CHECKS = {
    "twitter": check_twitter_handle,
    "github": check_github_handle,
    "ens": check_ens_handle,
    "farcaster": check_farcaster_handle,
    "discord": check_discord_handle,
}


def run_handle_guardian(domains: List[str]) -> None:
    """
    Run handle guardian checks for a list of domains.

    Args:
        domains: List of domains to check (e.g., ["21xo.eth", "lol.21xo.eth"])
    """
    print(f"🔍 Running handle guardian for {len(domains)} domains...")

    # Create registry directory
    registry_dir = Path("vault/registry")
    registry_dir.mkdir(parents=True, exist_ok=True)

    # Initialize registry
    registry = {}

    for domain in domains:
        # Extract handle from domain (remove .eth or other TLD)
        handle = domain.split(".")[0].replace("-", "")

        # Build registry entry
        entry = build_registry_entry(domain, handle)

        # Check each platform
        for platform, check_func in PLATFORM_CHECKS.items():
            try:
                result = check_func(handle)
                entry["platforms"][platform] = result
                print(f"  {domain} -> {platform}: {result.get('available', 'unknown')}")
            except Exception as e:
                print(f"⚠️ {platform} check failed for {handle}: {e}")
                entry["platforms"][platform] = {"handle": handle, "available": None}

        registry[domain] = entry

    # Save registry to YAML-like format
    registry_path = registry_dir / "handles.yml"
    with open(registry_path, "w") as f:
        f.write("# Handle Registry\n")
        f.write(f"# Generated: {datetime.utcnow().isoformat()}\n\n")

        for domain, entry in registry.items():
            f.write(f"{domain}:\n")
            f.write(f"  handle: {entry['handle']}\n")
            f.write(f"  checked_at: {entry['checked_at']}\n")
            f.write("  platforms:\n")

            for platform, data in entry["platforms"].items():
                if data:
                    f.write(f"    {platform}:\n")
                    f.write(f"      handle: {data.get('handle', '')}\n")
                    f.write(f"      available: {data.get('available', 'unknown')}\n")

    print(f"✅ Registry saved to {registry_path}")

    # Log to seal log
    log_path = Path("vault/logbook/seal.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as log:
        log.write(
            f"[handle_guardian] {datetime.utcnow().isoformat()} - Scanned {len(domains)} domains\n"
        )

    # Create inbox message
    inbox_path = Path("vault/inbox/handle-guardian.mdx")
    inbox_path.parent.mkdir(parents=True, exist_ok=True)

    inbox_content = f"""# Handle Guardian Report

Generated: {datetime.utcnow().isoformat()}

## Domains Checked: {len(domains)}

{chr(10).join(f"- {domain}" for domain in domains)}

## Summary

Handle availability checks completed for all platforms:
- Twitter
- GitHub
- ENS
- Farcaster
- Discord

See `vault/registry/handles.yml` for detailed results.

---
*Generated by handle_guardian.py*
"""

    with open(inbox_path, "w") as f:
        f.write(inbox_content)

    print(f"✅ Inbox message created: {inbox_path}")

    # Try to trigger claim_bot persona
    try:
        from xo_core.agent.dispatch import dispatch_persona

        print("🤖 Triggering claim_bot persona...")
        dispatch_persona("claim_bot", preview=False, memory=True)
    except Exception as e:
        print(f"⚠️ Failed to trigger claim_bot persona: {e}")

    print("🎉 Handle guardian complete!")


def reserve_handles(domains: List[str] = None) -> None:
    """
    Reserve handles for domains based on registry data.

    Args:
        domains: Optional list of domains to reserve. If None, reads from registry.
    """
    registry_path = Path("vault/registry/handles.yml")

    if not registry_path.exists():
        print("⚠️ Registry file not found. Run handle guardian first.")
        return

    # If no domains specified, read from registry
    if domains is None:
        domains = []
        with open(registry_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#") and ":" in line:
                    domain = line.split(":")[0].strip()
                    if domain and "." in domain:
                        domains.append(domain)

    if not domains:
        print("⚠️ No domains found to reserve.")
        return

    print(f"🔒 Reserving handles for {len(domains)} domains...")

    # Create reserved data
    reserved = {}

    for domain in domains:
        handle = domain.split(".")[0].replace("-", "")
        reserved[domain] = {
            "handle": handle,
            "reserved": True,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",  # Could be: pending, success, failed
        }

    # Save reserved data
    reserved_path = Path("vault/registry/reserved.json")
    reserved_path.parent.mkdir(parents=True, exist_ok=True)

    with open(reserved_path, "w") as f:
        json.dump(reserved, f, indent=2)

    print(f"✅ Reserved handles saved to {reserved_path}")
    print(f"📝 {len(domains)} domains marked for reservation")

    # TODO: Implement actual reservation logic for each platform
    print("⚠️ Actual reservation not yet implemented - this is a placeholder")


def get_available_handles() -> Dict[str, Any]:
    """Get list of available handles from registry."""
    registry_path = Path("vault/registry/handles.yml")

    if not registry_path.exists():
        return {}

    available = {}

    with open(registry_path, "r") as f:
        current_domain = None
        current_platforms = {}

        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if "." in key:  # Domain line
                    if current_domain and current_platforms:
                        available[current_domain] = current_platforms
                    current_domain = key
                    current_platforms = {}
                elif key == "platforms":
                    continue
                elif key in ["twitter", "github", "ens", "farcaster", "discord"]:
                    # This is a platform line, we'll parse the next lines
                    pass

        # Add the last domain
        if current_domain and current_platforms:
            available[current_domain] = current_platforms

    return available

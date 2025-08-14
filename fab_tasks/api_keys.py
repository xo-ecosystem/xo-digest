from pathlib import Path

import yaml
from invoke import task


CONFIG_PATH = Path("config/api_keys.yml")


def load_config():
    if CONFIG_PATH.exists():
        return yaml.safe_load(open(CONFIG_PATH)) or {}
    return {}


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f, sort_keys=False)


@task
def keys_add(c, key, tier="free"):
    """Add API key with tier."""
    cfg = load_config()
    cfg.setdefault("keys", {})[key] = tier
    save_config(cfg)
    print(f"✅ Added key '{key}' with tier '{tier}'")


@task
def keys_remove(c, key):
    """Remove API key."""
    cfg = load_config()
    if cfg.get("keys", {}).pop(key, None):
        save_config(cfg)
        print(f"🗑 Removed key '{key}'")
    else:
        print(f"⚠ Key '{key}' not found")

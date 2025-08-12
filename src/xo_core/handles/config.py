import os

ALLOWLIST = set(os.getenv("XO_HANDLE_ALLOWLIST", "brie").split(","))
FEATURE_ENABLED = os.getenv("XO_HANDLE_FEATURE", "1") == "1"
CLAIM_TTL_MIN = int(os.getenv("XO_HANDLE_CLAIM_TTL_MIN", "30"))
REGISTRY_DIR = os.getenv(
    "XO_HANDLE_REGISTRY_DIR", os.path.expanduser("~/.config/xo-core/handles")
)
VAULT_OUT_DIR = os.getenv("XO_VAULT_HANDLES_DIR", "vault/handles")

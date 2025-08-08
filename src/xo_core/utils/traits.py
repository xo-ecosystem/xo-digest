from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

import yaml


DROPS_DIR = Path("drops")


def _normalize_trait(raw: Any) -> Dict[str, Any]:
    """Return a normalized trait dict with expected keys.

    The function is defensive: if input is not a dict, it wraps it.
    """
    if not isinstance(raw, dict):
        return {
            "name": str(raw),
            "description": "",
            "rarity": "",
            "tags": [],
            "media": {},
            "game_effects": {},
        }

    trait: Dict[str, Any] = dict(raw)
    trait.setdefault("id", trait.get("name") or "unknown")
    trait.setdefault("name", "unnamed")
    trait.setdefault("description", "")
    trait.setdefault("rarity", "")
    trait.setdefault("tags", [])
    trait.setdefault("media", {})
    trait.setdefault("attributes", [])
    trait.setdefault("game_effects", {})
    return trait


def load_traits(drop_id: str) -> List[Dict[str, Any]]:
    """Load and normalize traits for a single drop from `.traits.yml`.

    Returns empty list if file does not exist or YAML invalid.
    """
    traits_path = DROPS_DIR / drop_id / ".traits.yml"
    if not traits_path.exists():
        # Fallback: some drops keep traits under hidden/.traits.yml
        hidden_path = DROPS_DIR / drop_id / "hidden" / ".traits.yml"
        if hidden_path.exists():
            traits_path = hidden_path
        else:
            return []

    try:
        with traits_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or []
    except yaml.YAMLError:
        return []

    if not isinstance(data, list):
        return []

    return [_normalize_trait(t) for t in data]


def index_traits() -> Dict[str, List[Dict[str, Any]]]:
    """Scan all drops and build an index of `drop_id -> traits`.

    A drop is a directory under `drops/` that contains a `.traits.yml` file.
    """
    index: Dict[str, List[Dict[str, Any]]] = {}
    if not DROPS_DIR.exists():
        return index

    for entry in sorted(DROPS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        drop_id = entry.name
        root_traits = entry / ".traits.yml"
        hidden_traits = entry / "hidden" / ".traits.yml"
        if root_traits.exists() or hidden_traits.exists():
            index[drop_id] = load_traits(drop_id)
    return index

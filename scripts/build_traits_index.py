#!/usr/bin/env python3
"""Build a static traits index JSON for frontend fallback.

Outputs to `xo-games/static/traits.index.json`.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.xo_core.utils.traits import index_traits


def main() -> None:
    root = Path.cwd()
    out_dir = root / "xo-games" / "static"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "traits.index.json"

    data = {"traits": index_traits()}
    out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"✅ Wrote {out_file}")


if __name__ == "__main__":
    main()

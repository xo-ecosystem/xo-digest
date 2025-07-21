

from fabric import task
from pathlib import Path
import json
import shutil

@task
def drop_webp(c, drop="eighth"):
    """
    Sync and archive .webp assets for a given drop.
    Assumes files are manually placed in drop.assets/.
    """
    drop_root = Path(f"src/xo_core/vault/seals/{drop}/drop.assets")
    webp_dir = drop_root / "webp"
    orig_dir = drop_root / "original"
    mj_dir = drop_root / "midjourney"
    preview_yaml = drop_root.parent / "_drop.yml"
    status_json = drop_root.parent / "metadata/000.status.json"

    webp_dir.mkdir(parents=True, exist_ok=True)
    orig_dir.mkdir(parents=True, exist_ok=True)
    mj_dir.mkdir(parents=True, exist_ok=True)

    # Archive matching files into original/ and midjourney/
    for f in drop_root.glob("*.webp"):
        if "midjourney" in f.name.lower():
            shutil.copy(f, mj_dir / f.name)
        else:
            shutil.copy(f, orig_dir / f.name)
        shutil.move(f, webp_dir / f.name)

    print(f"✅ Archived and organized .webp files for {drop}")

    # Update status JSON if exists
    if status_json.exists():
        with open(status_json, "r") as f:
            data = json.load(f)

        data["images"] = sorted([f.name for f in webp_dir.glob("*.webp")])

        with open(status_json, "w") as f:
            json.dump(data, f, indent=2)
        print("📄 Patched 000.status.json with image list.")

    # (Optional) Add YAML patching later if needed
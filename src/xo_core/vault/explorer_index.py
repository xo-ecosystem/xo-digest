

import json
from pathlib import Path
from xo_core.utils.pulse_loader import load_all_pulses
from xo_core.vault.ipfs_utils import log_status

def generate_explorer_index(output_path="vault/preview/index.json"):
    pulses = load_all_pulses()
    index_data = [
        {"slug": pulse["slug"], "title": pulse["title"]}
        for pulse in pulses
    ]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(index_data, f, indent=2)
    log_status("📦 Explorer index.json written with {} entries".format(len(index_data)))
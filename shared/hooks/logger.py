import json
from pathlib import Path
from datetime import datetime


def hook_logger(persona, webhook=False, preview=False, memory=False):
    """Logger plugin hook for tracking each dispatch"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "agent_dispatches.log"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "persona": persona,
        "hooks": {"webhook": webhook, "preview": preview, "memory": memory},
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"📝 Dispatch logged → {log_file}")

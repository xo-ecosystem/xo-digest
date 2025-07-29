import json
import os
from pathlib import Path
from datetime import datetime


def hook_memory(persona, data=None):
    """Memory plugin hook for persisting per-persona context"""
    memory_dir = Path(".memory")
    memory_dir.mkdir(exist_ok=True)

    memory_file = memory_dir / f"{persona}.json"

    # Load existing memory
    if memory_file.exists():
        with open(memory_file, "r") as f:
            memory = json.load(f)
    else:
        memory = {
            "persona": persona,
            "created": datetime.now().isoformat(),
            "sessions": [],
        }

    # Add new session
    session = {"timestamp": datetime.now().isoformat(), "data": data or {}}
    memory["sessions"].append(session)
    memory["last_updated"] = datetime.now().isoformat()

    # Save memory
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2)

    print(f"🧠 Memory updated → {memory_file} ({len(memory['sessions'])} sessions)")

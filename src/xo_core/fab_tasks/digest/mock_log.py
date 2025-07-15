from invoke import task
import datetime
import json
from pathlib import Path

@task
def write_mock_log(c):
    """Write a mock digest log entry to .logbook/."""
    log_dir = Path(".logbook")
    log_dir.mkdir(exist_ok=True)
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event": "digest.mock-log",
        "status": "success",
        "message": "Mock digest log written"
    }
    filename = log_dir / f"{log_entry['timestamp']}.json"
    with open(filename, "w") as f:
        json.dump(log_entry, f, indent=2)
    print(f"✅ Mock log written to {filename}")
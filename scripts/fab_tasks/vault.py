import datetime
import subprocess
from pathlib import Path

from invoke import task


@task
def archive(c):
    """
    🗂️ Archive signed vault files and upload to Arweave
    """
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = Path("vault/archive-log.txt")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    c.run("xo-fab sign-all", warn=True)

    result = c.run("./scripts/upload_to_arweave.sh", warn=True, hide=True)
    with log_file.open("a") as log:
        log.write(f"\n--- Archive {ts} ---\n")
        log.write(result.stdout)
        log.write(result.stderr)
        log.write("\n")

    print(f"✅ Archive complete. Logged to {log_file}")

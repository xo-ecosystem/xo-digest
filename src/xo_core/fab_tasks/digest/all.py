# src/xo_core/fab_tasks/digest/all.py
from invoke import task
import os
import subprocess
import time

@task
def all(c):
    print("🧠 Running full digest routine (digest.all)")

    start = time.time()

    # You can extend this with subtasks or logic later
    # Placeholder for digest logic

    duration = time.time() - start
    print("✅ Finished digest routine")

    subprocess.run([
        "python3", "scripts/send_webhook.py",
        "--event", "digest_publish",
        "--status", "success",
        "--sha", os.getenv("GIT_COMMIT_SHA", "local"),
        "--duration", str(round(duration, 2)),
        "--excerpt", "vault/daily/index.html",
        "--attach", "vault/daily/index.html"
    ])
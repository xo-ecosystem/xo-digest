from invoke import Collection

# Import tasks here

import os
import json
from pathlib import Path
from fabric import task

from xo_core.vault.ipfs_utils import pin_to_ipfs
import logging

logger = logging.getLogger(__name__)
from xo_core.utils.arweave_upload import upload_to_arweave
import shutil

@task
def push_logbook(c):
    log_dir = Path("vault/.logbook")
    if not log_dir.exists():
        print("📁 No .logbook/ directory found.")
        return

    logs = sorted(log_dir.glob("*.json"), reverse=True)
    if not logs:
        print("📄 No logbook JSON files to push.")
        return

    for log_file in logs[:5]:  # Pin the 5 most recent logs
        with open(log_file, "r") as f:
            content = f.read()
        print(f"📌 Pinning {log_file.name}...")
        try:
            ipfs_hash = pin_to_ipfs(str(log_file))
            logger.info(f"Pushed {log_file.name} to IPFS: {ipfs_hash}")
        except Exception as e:
            logger.error(f"Failed to pin {log_file.name}: {e}")
        
        # Replacing upload_to_arweave with subprocess to arweave-deploy
        import subprocess
        if shutil.which("arweave-deploy"):
            arweave_result = subprocess.run(
                ["arweave-deploy", str(log_file)],
                capture_output=True,
                text=True
            )
            logger.info(f"📤 Arweave TX for {log_file.name}: {arweave_result.stdout.strip()}")
        else:
            logger.warning(f"⚠️ Arweave-deploy not found. Skipping Arweave push for {log_file.name}.")
import os
import shutil

from fabric import task
from invoke import run

CSV_REPO_PATH = "/mnt/shield/fabric-tasks-repo/git/xo-core/domains/Domain_List.csv"
CSV_TARGET_PATH = "/mnt/shield/domains/Domain_List.csv"


@task
def pull_csv(c):
    """Pull the latest Domain_List.csv from Git to /mnt/shield/domains."""
    if os.path.exists(CSV_REPO_PATH):
        shutil.copy2(CSV_REPO_PATH, CSV_TARGET_PATH)
        print(f"✅ Domain list updated: {CSV_REPO_PATH} → {CSV_TARGET_PATH}")
    else:
        print(f"❌ CSV not found at expected repo path: {CSV_REPO_PATH}")

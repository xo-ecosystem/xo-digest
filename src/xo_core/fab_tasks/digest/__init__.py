"""Digest namespace for XO Core Fabric tasks."""

from invoke import Collection

from .push import push_digest
from .ipfs_upload import pin_digest_to_ipfs
from .webhook_trigger import trigger_digest_webhook
from .mock_log import write_mock_log
# from .vault_log import push_logbook  # ✅ This is now safe
from .digest_all import all as digest_all
import os
import subprocess
import time

# Create digest namespace
ns = Collection("digest")

# Register all digest tasks
ns.add_task(push_digest, name="push")
ns.add_task(pin_digest_to_ipfs, name="ipfs-upload")
ns.add_task(trigger_digest_webhook, name="webhook-trigger")
ns.add_task(write_mock_log, name="mock-log")
ns.add_task(digest_all, name="all")


try:
    @digest_all.add_wrapper
    def notify_after_digest_all(task_func):
        def wrapper(c, *args, **kwargs):
            start_time = time.time()
            result = task_func(c, *args, **kwargs)
            duration = int(time.time() - start_time)
            excerpt_path = "vault/daily/index.html"
            try:
                subprocess.run([
                    "python3", "scripts/send_webhook.py",
                    "--event", "digest_publish",
                    "--status", "success",
                    "--sha", os.getenv("GIT_COMMIT_SHA", "local"),
                    "--duration", str(duration),
                    "--excerpt", excerpt_path,
                    "--attach", excerpt_path
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Webhook failed: {e}")
            return result
        return wrapper
except Exception:
    pass


__all__ = ["ns"]
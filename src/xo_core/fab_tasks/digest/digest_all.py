from invoke import task
import subprocess
import time
import os
# from xo_core.vault.inbox_render import render_all_inbox_to_html
from xo_core.vault.digest_gen import generate_digest

@task
def all(c):
    """
    Run the full digest generation pipeline:
    - Inbox HTML rendering
    - Digest .md and .html generation
    - Optional webhook notify
    """
    start_time = time.time()

    print("📥 Rendering inbox to HTML...")
    render_all_inbox_to_html()

    print("📜 Generating digest...")
    excerpt_path = generate_digest()

    duration = int(time.time() - start_time)

    try:
        subprocess.run([
            "python3", "scripts/send_webhook.py",
            "--event", "digest_publish",
            "--status", "success",
            "--sha", os.getenv("GIT_COMMIT_SHA", "local"),
            "--duration", str(duration),
            "--excerpt", excerpt_path,
            "--attach", "vault/daily/index.html"
        ], check=True)
    except Exception as e:
        print(f"⚠️ Webhook notification failed: {e}")
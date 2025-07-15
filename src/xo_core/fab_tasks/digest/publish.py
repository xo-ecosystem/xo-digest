from invoke import task, Collection
from xo_core.fab_tasks.digest.push import push_digest
from xo_core.fab_tasks.digest.vault_log import log_digest_to_vault
from xo_core.fab_tasks.digest.ipfs_upload import pin_digest_to_ipfs
from xo_core.fab_tasks.digest.webhook_trigger import trigger_digest_webhook

@task(name="all")
def publish_all_digest(ctx, slim="false", local="false"):
    """
    Run the full digest publish pipeline with optional flags.
    """
    slim_flag = slim.lower() in ("true", "1", "yes")
    local_flag = local.lower() in ("true", "1", "yes")

    print("🚀 Starting full XO Digest publish flow...")
    print(f"🔧 Flags: slim={slim_flag}, local={local_flag}")
    ctx.config.run.echo = True
    push_digest(ctx)

    log_digest_to_vault(ctx)

    if not local_flag:
        pin_digest_to_ipfs(ctx)

    if not slim_flag:
        trigger_digest_webhook(ctx)

    print("✅ XO Digest publish flow complete!")

    # ✅ Log result to Vault logbook
    import json, os
    from datetime import datetime

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "flags": {"slim": slim_flag, "local": local_flag},
        "status": "success",
    }

    os.makedirs(".logbook", exist_ok=True)
    log_path = ".logbook/last_digest.json"
    with open(log_path, "w") as f:
        json.dump(log_entry, f, indent=2)

    print(f"🗂️  Digest log written to {log_path}")

ns = Collection("digest")
ns.add_task(publish_all_digest, name="all")
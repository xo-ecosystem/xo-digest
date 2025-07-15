from invoke import task, Collection

@task
def clear_cache(ctx):
    """
    Clear Cloudflare cache via API (placeholder).
    """
    print("🧹 Clearing Cloudflare cache...")

@task
def purge_dns(ctx):
    """
    Purge Cloudflare DNS records (placeholder).
    """
    print("🧼 Purging Cloudflare DNS records...")

ns = Collection("cloudflare-utils.api-utils")
ns.add_task(clear_cache)
ns.add_task(purge_dns)

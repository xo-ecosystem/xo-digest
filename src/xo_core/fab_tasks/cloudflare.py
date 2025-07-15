# fab_tasks/cloudflare.py
import os
import shutil
from datetime import datetime

import requests
from invoke import Collection, task
from tools.cloudflare.api_utils import (API_BASE, HEADERS, export_zone,
                                        get_zone_id)
from tools.cloudflare.import_utils import import_zone


@task(
    help={
        "versioned": "Save a timestamped copy of the snapshot",
        "backup": "Backup existing snapshot before export",
    }
)
def zone_export(c, domain, versioned=True, backup=True):
    """
    📦 Export Cloudflare zone config for a domain.
    Usage: xo-fab cloudflare.zone_export:xo-verses.com --versioned=True --backup=True
    """
    snapshot_path = f"zone_snapshots/{domain}.json"

    # Backup existing snapshot
    if backup and os.path.exists(snapshot_path):
        os.rename(snapshot_path, f"{snapshot_path}.bak")
        print(f"🗂️  Existing snapshot backed up: {snapshot_path}.bak")

    # Perform export
    export_zone(domain)

    # Create versioned copy
    if versioned:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        tagged = f"zone_snapshots/{domain}@{timestamp}.json"
        shutil.copy(snapshot_path, tagged)
        print(f"📌 Versioned snapshot saved: {tagged}")


@task(help={"dry_run": "Print diff and actions without applying changes"})
def zone_import(c, domain, dry_run=False):
    """
    ♻️ Import Cloudflare zone config from snapshot.
    Usage: xo-fab cloudflare.zone_import:xo-verses.com --dry_run=True
    """
    import_zone(domain, dry_run=dry_run)


@task(help={"dry_run": "Print diff and actions without applying changes"})
def zone_import_all(c, dry_run=False):
    """
    ♻️ Import all Cloudflare zone snapshots in zone_snapshots/
    Usage: xo-fab cloudflare.zone_import_all --dry_run=True
    """
    for fname in os.listdir("zone_snapshots"):
        if fname.endswith(".json"):
            domain = fname[:-5]
            print(f"⏳ Importing zone: {domain}")
            import_zone(domain, dry_run=dry_run)


@task
def purge_cache(c, domain):
    """
    🚿 Purge Cloudflare cache for a given domain.
    Usage: xo-fab cloudflare.purge_cache:xo-verses.com
    """
    zone_id = get_zone_id(domain)
    url = f"{API_BASE}/zones/{zone_id}/purge_cache"
    resp = requests.post(url, headers=HEADERS, json={"purge_everything": True})
    if resp.ok:
        print(f"✅ Cache purged for {domain}")
    else:
        print(
            f"❌ Failed to purge cache for {domain}: {resp.status_code} - {resp.text}"
        )


# Module-level namespace declaration for dynamic loader
namespace = Collection("cloudflare")
namespace.add_task(zone_export, name="zone_export")
namespace.add_task(zone_export, name="zone-export")
namespace.add_task(zone_import, name="zone_import")
namespace.add_task(zone_import, name="zone-import")
namespace.add_task(zone_import_all, name="zone_import_all")
namespace.add_task(zone_import_all, name="zone-import-all")
namespace.add_task(purge_cache, name="purge_cache")
namespace.add_task(purge_cache, name="purge-cache")


from invoke import Collection
ns = Collection("cloudflare")
ns.add_task(zone_import, name="zone_import")
ns.add_task(zone_import_all, name="zone_import_all")
ns.add_task(purge_cache, name="purge_cache")
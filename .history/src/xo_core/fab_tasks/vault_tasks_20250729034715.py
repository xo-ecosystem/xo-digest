from invoke import Collection, task
from xo_core.vault import community_tasks


@task
def bundle(c, name):
    print(f"📦 Bundling vault package: {name}")
    c.run(f"mkdir -p vault/bundles/{name}")
    c.run(f"cp -r vault/daily/{name} vault/bundles/{name}")
    print(f"✅ Vault bundle created at vault/bundles/{name}")


@task
def archive(c, name):
    print(f"🗃 Archiving vault package: {name}")
    c.run(f"mkdir -p vault/archive/")
    c.run(f"cp -r vault/bundles/{name} vault/archive/")
    print(f"📦 Bundle {name} archived to vault/archive/")


@task
def sign_all(c):
    print("🧾 Signing all .coin.yml and .mdx files in vault/")
    # Insert logic here


@task
def explorer_deploy(c):
    print("🚀 Deploying vault explorer")
    # Insert logic here


@task
def digest_export(c):
    """Copy digest output to public viewer directory."""
    c.run("mkdir -p webapp/digest/vault/daily")
    c.run("cp -r vault/daily/* webapp/digest/vault/daily/")
    print("📤 Digest exported to webapp/digest/vault/daily/")


# Community tasks
@task(
    help={
        "slug": "Pulse slug to render",
        "output_dir": "Output directory for HTML files",
    }
)
def inbox_render(c, slug=None, output_dir="vault/daily"):
    """Render inbox comments to HTML."""
    community_tasks.inbox_render(c, slug, output_dir)


@task(help={"slug": "Pulse slug to analyze", "create_pulse": "Create reply pulse"})
def agent_reply_suggest(c, slug=None, create_pulse=False):
    """Analyze inbox and suggest replies."""
    community_tasks.agent_reply_suggest(c, slug, create_pulse)


@task(
    help={
        "slug": "Pulse slug",
        "channels": "Comma-separated channels",
        "filters": "Comma-separated filters",
        "health_check": "Broadcast health check",
    }
)
def signal_broadcast(c, slug=None, channels="inbox", filters=None, health_check=False):
    """Broadcast social signals."""
    community_tasks.signal_broadcast(c, slug, channels, filters, health_check)


@task(help={"slug": "Pulse slug", "all_features": "Activate all features"})
def community_activate(c, slug=None, all_features=False):
    """Activate all community features for a slug."""
    community_tasks.community_activate(c, slug, all_features)


@task
def community_status(c):
    """Show community system status."""
    community_tasks.community_status(c)


@task
def digest_index(c):
    """Generate index.json for vault/daily digest viewer."""
    import json, os

    entries = []
    for root, dirs, files in os.walk("vault/daily"):
        for file in files:
            if file.endswith(".mdx"):
                slug = file.replace(".mdx", "")
                entries.append({"slug": slug, "title": slug.replace("_", " ").title()})
    with open("vault/daily/index.json", "w") as f:
        json.dump(entries, f, indent=2)
    print(f"📦 index.json generated with {len(entries)} entries.")


# Create namespace
ns = Collection("vault")

# Add local tasks
ns.add_task(sign_all, name="sign-all")
ns.add_task(explorer_deploy, name="explorer-deploy")
ns.add_task(digest_export, name="digest-export")
ns.add_task(digest_index, name="digest-index")
ns.add_task(bundle)
ns.add_task(archive)

# Add community tasks
ns.add_task(inbox_render, name="inbox-render")
ns.add_task(agent_reply_suggest, name="agent-reply-suggest")
ns.add_task(signal_broadcast, name="signal-broadcast")
ns.add_task(community_activate, name="community-activate")
ns.add_task(community_status, name="community-status")

# Import and add external modules
try:
    from .vault_sign import ns as vault_sign_ns

    ns.add_collection(vault_sign_ns, name="sign")
except ImportError as e:
    print(f"⚠️ Could not import vault_sign: {e}")

try:
    from .vault_explorer_preview import ns as explorer_ns

    ns.add_collection(explorer_ns, name="explorer")
except ImportError as e:
    print(f"⚠️ Could not import vault_explorer_preview: {e}")

try:
    from .vault_pulse_sync import ns as pulse_sync_ns

    ns.add_collection(pulse_sync_ns, name="pulse")
except ImportError as e:
    print(f"⚠️ Could not import vault_pulse_sync: {e}")

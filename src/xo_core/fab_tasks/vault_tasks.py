from invoke import Collection, task
from xo_core.vault import community_tasks


@task(help={"slug": "Name of the file to sign (without extension)"})
def sign(c, slug):
    print(f"🔐 Signing vault file: {slug}")
    # Insert logic here


@task
def sign_all(c):
    print("🧾 Signing all .coin.yml and .mdx files in vault/")
    # Insert logic here


@task
def explorer_deploy(c):
    print("🚀 Deploying vault explorer")
    # Insert logic here


# Community tasks
@task(help={"slug": "Pulse slug to render", "output_dir": "Output directory for HTML files"})
def inbox_render(c, slug=None, output_dir="vault/daily"):
    """Render inbox comments to HTML."""
    community_tasks.inbox_render(c, slug, output_dir)


@task(help={"slug": "Pulse slug to analyze", "create_pulse": "Create reply pulse"})
def agent_reply_suggest(c, slug=None, create_pulse=False):
    """Analyze inbox and suggest replies."""
    community_tasks.agent_reply_suggest(c, slug, create_pulse)


@task(help={"slug": "Pulse slug", "channels": "Comma-separated channels", "filters": "Comma-separated filters", "health_check": "Broadcast health check"})
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


ns = Collection("vault")
ns.add_task(sign)
ns.add_task(sign_all, name="sign-all")
ns.add_task(explorer_deploy, name="explorer-deploy")

# Add community tasks
ns.add_task(inbox_render, name="inbox.render")
ns.add_task(agent_reply_suggest, name="agent.reply-suggest")
ns.add_task(signal_broadcast, name="signal.broadcast")
ns.add_task(community_activate, name="community.activate")
ns.add_task(community_status, name="community.status")

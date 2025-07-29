from invoke import Collection, task
import os
import subprocess

# Import task modules with proper namespace structure
from fab_tasks.dns_check_21xo import ns as dns_ns
from fab_tasks.deploy import ns as deploy_ns
from fab_tasks.patch import ns as patch_ns
from fab_tasks.dynamic_loader import ns as loader_ns

# Import vault tasks
# try:
#     from src.xo_core.fab_tasks.vault_tasks import ns as vault_ns
# except ImportError as e:
#     print(f"⚠️ Could not import vault tasks: {e}")
#     vault_ns = None
vault_ns = None


@task
def deploy_prod(c):
    """Deploy dev code to production clone at ~/xo-core"""
    dev_path = os.getcwd()
    prod_path = os.path.expanduser("~/xo-core")

    if not os.path.isdir(prod_path):
        print("❌ Production folder not found at ~/xo-core")
        return

    print("🚀 Deploying from dev to production...")
    os.system(
        f'rsync -av --exclude ".git" --exclude ".env*" --exclude "__pycache__" {dev_path}/ {prod_path}/'
    )
    print("✅ Sync complete.")


@task
def dispatch(c, persona=None, preview=False, webhook=False, memory=False):
    """
    CLI task to dispatch a persona with optional webhook, preview, and memory support.
    """
    from xo_core.agent.dispatch import dispatch_persona

    dispatch_persona(persona=persona, preview=preview, webhook=webhook, memory=memory)


@task
def wire_hooks(c):
    """
    Wire the agent webhook and inbox plugin handlers.
    """
    from xo_core.agent.hooks import wire_hooks

    wire_hooks()


@task
def cosmic_align(c, dry_run=False):
    """
    🌌 Cosmic alignment - full system check and sync.

    Args:
        dry_run (bool): Only show what would be done, don't perform actions
    """
    print("🌌 XO Core Cosmic Alignment")
    print("=" * 50)

    # Import tasks dynamically to avoid circular imports
    from fab_tasks.dns_check_21xo import (
        check_dns,
        sync_env_subdomains,
        generate_all_dns_artifacts,
    )
    from fab_tasks.deploy import health_check, log_deploy_status

    # 1. DNS Check
    print("\n1️⃣ DNS Configuration Check...")
    check_dns(c, dry_run=dry_run, validate_resolution=True)

    # 2. Environment Sync
    print("\n2️⃣ Environment Variable Sync...")
    sync_env_subdomains(c, dry_run=dry_run)

    # 3. Service Health Check
    print("\n3️⃣ Service Health Check...")
    services = ["vault", "inbox", "preview", "agent0"]
    for service in services:
        health_check(c, service=service)

    # 4. Deployment Status
    print("\n4️⃣ Deployment Status Logging...")
    for service in services:
        log_deploy_status(c, service=service)

    # 5. Generate DNS Artifacts
    print("\n5️⃣ Generating DNS Artifacts...")
    generate_all_dns_artifacts(c)

    print("\n✅ Cosmic alignment complete!")


@task
def dashboard_sync(c):
    """
    🔄 Sync dashboard artifacts and commit changes.
    """
    print("🔄 Syncing dashboard artifacts...")

    # Import dynamically to avoid circular imports
    from fab_tasks.dns_check_21xo import generate_all_dns_artifacts

    # Generate DNS artifacts
    generate_all_dns_artifacts(c)

    # Commit changes
    try:
        subprocess.run(["git", "add", "public/", ".deploy-log.json"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "🔄 Auto-sync dashboard artifacts"], check=True
        )
        print("✅ Committed dashboard artifacts")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Could not commit: {e}")

    print("✅ Dashboard sync complete!")


# Create agent namespace
agent_ns = Collection("agent")
agent_ns.add_task(dispatch, "dispatch")
agent_ns.add_task(wire_hooks, "wire-hooks")

# Create dashboard namespace
dashboard_ns = Collection("dashboard")
dashboard_ns.add_task(dashboard_sync, "sync")

# Main namespace
ns = Collection()
ns.add_collection(agent_ns)
ns.add_collection(dns_ns)
ns.add_collection(deploy_ns)
ns.add_collection(patch_ns)
ns.add_collection(loader_ns)
ns.add_collection(dashboard_ns)

# Add vault namespace if available
if vault_ns:
    ns.add_collection(vault_ns)

# Individual tasks
ns.add_task(deploy_prod, "deploy-prod")
ns.add_task(cosmic_align, "cosmic-align")

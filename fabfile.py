# [o3-fix 2025-08-03] Boot order fix and docs namespace wiring
from invoke import Collection, task
import os
import subprocess

# Import task modules with proper namespace structure
from fab_tasks.dns_check_21xo import ns as dns_ns
from fab_tasks.deploy import ns as deploy_ns
from fab_tasks.patch import ns as patch_ns
from fab_tasks.dynamic_loader import ns as loader_ns
from fab_tasks.vault_check import vault_check

# [o3-fix 2025-08-04] Temporarily comment out to resolve path conflicts
# from xo_core.fab_tasks.fix_loader import run_safe_loader
from xo_core.fab_tasks.docs import ns as docs_ns  # [o3-fix 2025-08-03]
from xo_core.fab_tasks.verify_tasks import ns as verify_ns  # [o3-fix 2025-08-04]
from xo_core.fab_tasks.chain_tasks import ns as chain_ns  # [o3-fix 2025-08-04]
from xo_core.fab_tasks.agent_tasks import ns as agent_cosmic_ns  # [o3-fix 2025-08-04]
from xo_core.fab_tasks.drop_tasks import ns as drop_ns  # [o3-fix 2025-08-04]
from xo_core.fab_tasks.agent_tasks import explore_drop

# Load namespaced tasks dynamically with logging
# [o3-fix 2025-08-03] Removed dynamic loader auto-load to ensure root Collection is defined first

try:
    from xo_core.fab_tasks.vault_tasks import ns as vault_ns
except ImportError as e:
    print(f"⚠️ Could not import vault tasks: {e}")
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
def deploy_vault_api(c, environment="production"):
    """
    🚀 Deploy XO Vault API to production.

    Args:
        environment: Deployment environment (production, staging, development)
    """
    print(f"🚀 Deploying XO Vault API to {environment}...")

    # Build and deploy using Docker Compose
    try:
        # Build the XO Vault API
        c.run("docker-compose -f docker-compose.xo.yml build xo-vault-api")

        # Deploy the stack
        c.run("docker-compose -f docker-compose.xo.yml up -d")

        print("✅ XO Vault API deployed successfully!")
        print("📊 Services:")
        print("   - XO Vault API: http://localhost:8801")
        print("   - HashiCorp Vault: http://localhost:8200")
        print("   - XO Node: http://localhost:8080")
        print("   - API Docs: http://localhost:8801/docs")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        exit(1)


@task
def vault_status(c):
    """🔍 Check XO Vault system status."""
    print("🔍 Checking XO Vault system status...")

    try:
        # Check XO Vault API
        try:
            import requests
        except ImportError:
            print("❌ requests library not available")
            return

        response = requests.get("http://localhost:8801/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ XO Vault API: {data['status']}")
            print(
                f"   - HashiCorp Vault: {'Connected' if data['vault_connected'] else 'Disconnected'}"
            )
            print(f"   - Version: {data['version']}")
        else:
            print("❌ XO Vault API: Unhealthy")
    except Exception as e:
        print(f"❌ XO Vault API: {e}")

    try:
        # Check HashiCorp Vault
        response = requests.get("http://localhost:8200/v1/sys/seal-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = "Unsealed" if not data.get("sealed", True) else "Sealed"
            print(f"✅ HashiCorp Vault: {status}")
        else:
            print("❌ HashiCorp Vault: Unreachable")
    except Exception as e:
        print(f"❌ HashiCorp Vault: {e}")


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


@task
def agent_health_check(c):
    """Check agent system health and availability"""
    print("🩺 Checking XO Agent system health...")

    try:
        import requests

        # Check local agent health endpoint
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Local Agent: {data.get('status', 'unknown')}")
                print(f"   Message: {data.get('msg', 'N/A')}")
            else:
                print(f"⚠️ Local Agent: HTTP {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ Local Agent: Not running or unreachable")

        # Check production agent endpoint
        agent_url = os.getenv("XO_AGENT0_URL", "https://agent0.21xo.com")
        try:
            response = requests.get(f"{agent_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Production Agent: {data.get('status', 'unknown')}")
            else:
                print(f"⚠️ Production Agent: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Production Agent: {e}")

        print("✅ Agent health check completed")

    except ImportError:
        print("❌ requests library not available")


agent_ns.add_task(agent_health_check, "health-check")
agent_ns.add_task(explore_drop, "explore_drop")

# Create dashboard namespace
dashboard_ns = Collection("dashboard")
dashboard_ns.add_task(dashboard_sync, "sync")
# [o3-fix 2025-08-03] Temporarily disable loader until we debug the Task/Collection mixing issue
# loader_ns = run_safe_loader()

# Main namespace
ns = Collection()
ns.add_collection(agent_ns)
ns.add_collection(dns_ns)
ns.add_collection(deploy_ns)
ns.add_collection(patch_ns)
ns.add_collection(dashboard_ns)
ns.add_collection(docs_ns)  # [o3-fix 2025-08-03] expose docs namespace
ns.add_collection(verify_ns)  # [o3-fix 2025-08-04] expose verify namespace
ns.add_collection(chain_ns)  # [o3-fix 2025-08-04] expose chain namespace
ns.add_collection(agent_cosmic_ns)  # [o3-fix 2025-08-04] expose cosmic agent namespace
ns.add_collection(drop_ns)  # [o3-fix 2025-08-04] expose drop management namespace
# ns.add_collection(loader_ns, name="loader")

# Add vault namespace if available
if vault_ns:
    ns.add_collection(vault_ns)

# Individual tasks
ns.add_task(deploy_prod, "deploy-prod")
ns.add_task(cosmic_align, "cosmic-align")
ns.add_task(vault_check, "vault-check")

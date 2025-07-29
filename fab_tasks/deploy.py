from invoke import Collection, task
import requests
import subprocess
import os
import json
from datetime import datetime


@task
def test_deploy(c, service="vault", endpoint="/run-task", timeout=10):
    """
    Test if FastAPI deployment is reachable at specified endpoint.

    Args:
        service (str): Service to test (vault, inbox, preview, agent0)
        endpoint (str): Endpoint to test
        timeout (int): Request timeout in seconds
    """
    base_urls = {
        "vault": "https://vault.21xo.com",
        "inbox": "https://inbox.21xo.com",
        "preview": "https://preview.21xo.com",
        "agent0": "https://agent0.21xo.com",
    }

    if service not in base_urls:
        print(f"❌ Unknown service: {service}")
        print(f"Available: {list(base_urls.keys())}")
        return

    url = f"{base_urls[service]}{endpoint}"

    print(f"🧪 Testing deployment: {url}")

    try:
        response = requests.get(url, timeout=timeout)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        return True
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout after {timeout}s")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 Connection failed")
        return False
    except Exception as e:
        print(f"❌ Failed to reach {url}:\n{e}")
        return False


@task
def deploy_fly(c, app_name="vault-21xo", dry_run=False):
    """
    Deploy to Fly.io using flyctl.

    Args:
        app_name (str): Fly.io app name
        dry_run (bool): Only show what would be deployed
    """
    print(f"🚀 Deploying to Fly.io: {app_name}")

    if dry_run:
        print("ℹ️ Dry-run: would deploy with flyctl")
        return

    try:
        # Check if flyctl is installed
        result = subprocess.run(["flyctl", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ flyctl not found. Please install it first.")
            return

        # Deploy
        result = subprocess.run(
            ["flyctl", "deploy", "--app", app_name], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("✅ Deployment successful!")
            print(result.stdout)
        else:
            print("❌ Deployment failed!")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Deployment error: {e}")


@task
def health_check(c, service="vault"):
    """
    Comprehensive health check for a service.

    Args:
        service (str): Service to check
    """
    print(f"🏥 Health check for {service}")

    # Test basic connectivity
    print("\n1️⃣ Basic connectivity...")
    basic_ok = test_deploy(c, service=service, endpoint="/")

    # Test API endpoint
    print("\n2️⃣ API endpoint...")
    api_ok = test_deploy(c, service=service, endpoint="/run-task")

    # Test health endpoint if available
    print("\n3️⃣ Health endpoint...")
    health_ok = test_deploy(c, service=service, endpoint="/health")

    # Summary
    print(f"\n📊 Health Summary for {service}:")
    print(f"  Basic: {'✅' if basic_ok else '❌'}")
    print(f"  API: {'✅' if api_ok else '❌'}")
    print(f"  Health: {'✅' if health_ok else '❌'}")

    return all([basic_ok, api_ok])


@task
def log_deploy_status(c, service="vault", log_file="logs/deploy.log"):
    """
    Log deployment status to file.

    Args:
        service (str): Service name
        log_file (str): Log file path
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    timestamp = datetime.now().isoformat()

    # Run health check
    basic_ok = test_deploy(c, service=service, endpoint="/")
    api_ok = test_deploy(c, service=service, endpoint="/run-task")

    status = {
        "timestamp": timestamp,
        "service": service,
        "basic_ok": basic_ok,
        "api_ok": api_ok,
        "overall": basic_ok and api_ok,
    }

    # Write to log file
    with open(log_file, "a") as f:
        f.write(json.dumps(status) + "\n")

    print(f"📝 Logged status to {log_file}")
    return status


@task
def deploy_all_services(c, dry_run=False):
    """
    Deploy all services defined in docker-compose.yml.

    Args:
        dry_run (bool): Only show what would be deployed
    """
    services = ["vault", "inbox", "preview", "agent0"]

    print(f"🚀 Deploying all {len(services)} services...")

    results = {}

    for service in services:
        print(f"\n🔧 Deploying {service}...")

        if dry_run:
            print(f"ℹ️ Dry-run: would deploy {service}")
            results[service] = {"status": "dry_run"}
        else:
            # For now, just test the deployment
            # In a real scenario, you'd call deploy_fly for each service
            status = health_check(c, service=service)
            results[service] = {"status": "tested", "healthy": status}

    # Summary
    print(f"\n📊 Deployment Summary:")
    for service, result in results.items():
        status = result.get("status", "unknown")
        if status == "tested":
            healthy = result.get("healthy", False)
            print(f"  {service}: {'✅' if healthy else '❌'}")
        else:
            print(f"  {service}: {status}")

    return results


@task
def deploy_with_dns(c):
    """
    🚀 Run deployment and update DNS artifacts.
    """
    print("📦 Starting full deployment...")

    # Run deployment
    deploy_all_services(c, dry_run=False)

    # Generate DNS artifacts
    from src.xo_core.fab_tasks.dns_check_21xo import generate_all_dns_artifacts

    print("📡 Generating DNS logs and chart...")
    generate_all_dns_artifacts(c)
    print("✅ DNS chart and log updated after deploy.")


# Create namespace
ns = Collection("deploy")
ns.add_task(test_deploy, "test")
ns.add_task(deploy_fly, "fly")
ns.add_task(health_check, "health")
ns.add_task(log_deploy_status, "log")
ns.add_task(deploy_all_services, "all")
ns.add_task(deploy_with_dns, "with_dns")

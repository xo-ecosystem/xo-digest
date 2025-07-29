#!/usr/bin/env python3
"""
🔐 XO Agent Deployment Script
Deploy the XO Agent system to GitHub and trigger deployment via webhook
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime


def run_command(cmd, check=True, capture_output=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, check=check, capture_output=capture_output, text=True
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return e


def load_env_production():
    """Load environment variables from .env.production."""
    env_file = Path(".env.production")
    if not env_file.exists():
        print("⚠️ .env.production not found, using current environment")
        return {}

    env_vars = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value
    return env_vars


def commit_to_github():
    """Commit changes to GitHub."""
    print("🔐 Vault Keeper: Committing changes to GitHub...")

    # Add all files
    run_command("git add .")

    # Commit with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    commit_msg = f"🔐 XO Agent refactor complete - {timestamp}"
    run_command(f'git commit -m "{commit_msg}"')

    # Push to main branch
    run_command("git push origin main")

    print("✅ Changes committed and pushed to GitHub")


def trigger_webhook_deployment(env_vars):
    """Trigger deployment via webhook."""
    print("🔐 Vault Keeper: Triggering webhook deployment...")

    # Get webhook URL from environment
    webhook_url = env_vars.get(
        "XO_AGENT_WEBHOOK_URL", "https://vault.21xo.com/agent/webhook"
    )
    agent_secret = env_vars.get("XO_AGENT_SECRET")

    if not agent_secret:
        print("⚠️ XO_AGENT_SECRET not found in .env.production")
        return False

    # Prepare webhook payload
    payload = {"task": "cosmic.align", "args": [False], "kwargs": {}}  # dry_run=False

    headers = {"Content-Type": "application/json", "X-Agent-Secret": agent_secret}

    try:
        print(f"🚀 Sending webhook to: {webhook_url}")
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            print("✅ Webhook deployment triggered successfully")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Webhook request failed: {e}")
        return False


def trigger_github_workflow(env_vars):
    """Trigger GitHub Actions workflow for deployment."""
    print("🔐 Vault Keeper: Triggering GitHub Actions workflow...")

    github_token = env_vars.get("GITHUB_TOKEN")
    if not github_token:
        print("⚠️ GITHUB_TOKEN not found in .env.production")
        return False

    # GitHub API endpoint for repository dispatch
    api_url = "https://api.github.com/repos/xo-verses/xo-agent/dispatches"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    payload = {
        "event_type": "webhook-trigger",
        "client_payload": {
            "task": "cosmic.align",
            "args": ["false"],  # dry_run=false
            "webhook_url": env_vars.get(
                "XO_AGENT_WEBHOOK_URL", "https://vault.21xo.com/agent/webhook"
            ),
        },
    }

    try:
        print(f"🚀 Triggering GitHub workflow...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)

        if response.status_code == 204:
            print("✅ GitHub workflow triggered successfully")
            return True
        else:
            print(f"❌ GitHub workflow failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ GitHub workflow request failed: {e}")
        return False


def deploy_to_fly(env_vars):
    """Deploy to Fly.io."""
    print("🔐 Vault Keeper: Deploying to Fly.io...")

    fly_token = env_vars.get("FLY_API_TOKEN")
    if not fly_token:
        print("⚠️ FLY_API_TOKEN not found in .env.production")
        return False

    # Set Fly.io token
    os.environ["FLY_API_TOKEN"] = fly_token

    # Deploy to Fly.io
    result = run_command("flyctl deploy --app xo-agent")

    if result.returncode == 0:
        print("✅ Fly.io deployment successful")
        return True
    else:
        print("❌ Fly.io deployment failed")
        return False


def main():
    """Main deployment function."""
    print("🔐 Vault Keeper: Starting XO Agent deployment...")
    print("=" * 60)

    # Load environment variables
    env_vars = load_env_production()
    print(f"📋 Loaded {len(env_vars)} environment variables")

    # Step 1: Commit to GitHub
    try:
        commit_to_github()
    except Exception as e:
        print(f"❌ GitHub commit failed: {e}")
        return False

    # Step 2: Trigger deployment (choose one method)
    deployment_method = os.getenv("DEPLOYMENT_METHOD", "webhook")

    if deployment_method == "webhook":
        success = trigger_webhook_deployment(env_vars)
    elif deployment_method == "github":
        success = trigger_github_workflow(env_vars)
    elif deployment_method == "fly":
        success = deploy_to_fly(env_vars)
    else:
        print(f"⚠️ Unknown deployment method: {deployment_method}")
        success = False

    if success:
        print("\n🎉 XO Agent deployment completed successfully!")
        print("🔐 Vault Keeper: Digital essence preserved and deployed!")
    else:
        print("\n❌ XO Agent deployment failed!")
        print(
            "🔐 Vault Keeper: Digital essence compromised - manual intervention required!"
        )

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Direct agent health check script.
Bypasses fabric runtime config issues.
"""

import os
import sys
import requests
from pathlib import Path


def agent_health_check():
    """Check agent system health and availability"""
    print("🩺 Checking XO Agent system health...")

    try:
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
        return True

    except ImportError:
        print("❌ requests library not available")
        return False


if __name__ == "__main__":
    success = agent_health_check()
    sys.exit(0 if success else 1)

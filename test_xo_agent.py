#!/usr/bin/env python3
"""
🔐 XO Agent Test Script
Test the XO Agent system before deployment
"""

import sys
import os
from pathlib import Path


def test_imports():
    """Test all critical imports."""
    print("🔐 Vault Keeper: Testing imports...")

    tests = [
        ("xo_agents.web.webhook_router", "router"),
        ("xo_agents.web.tasks", "get_available_tasks"),
        ("xo_agents.web.middleware", "verify_agent_secret"),
        ("xo_agents.api", "app"),
        ("main", "app"),
    ]

    all_passed = True

    for module_name, attr_name in tests:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            if hasattr(module, attr_name):
                print(f"✅ {module_name}.{attr_name}: OK")
            else:
                print(f"❌ {module_name}.{attr_name}: Missing attribute")
                all_passed = False
        except Exception as e:
            print(f"❌ {module_name}.{attr_name}: {e}")
            all_passed = False

    return all_passed


def test_task_registry():
    """Test the task registry."""
    print("\n🔐 Vault Keeper: Testing task registry...")

    try:
        from xo_agents.web.tasks import get_available_tasks

        tasks = get_available_tasks()

        print(f"✅ Task registry loaded: {len(tasks)} tasks")
        print("Available tasks:")
        for task_name, task_info in tasks.items():
            print(f"  - {task_name}: {task_info['description']}")

        return True
    except Exception as e:
        print(f"❌ Task registry test failed: {e}")
        return False


def test_webhook_endpoints():
    """Test webhook endpoints."""
    print("\n🔐 Vault Keeper: Testing webhook endpoints...")

    try:
        from xo_agents.web.webhook_router import router

        # Check if router has expected endpoints
        expected_routes = [
            "/webhook",
            "/test",
            "/tasks",
            "/health",
            "/echo",
            "/run-task",
        ]

        routes = [route.path for route in router.routes]
        print(f"✅ Router has {len(routes)} routes")

        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"✅ Route {expected}: Found")
            else:
                print(f"❌ Route {expected}: Missing")
                return False

        return True
    except Exception as e:
        print(f"❌ Webhook endpoints test failed: {e}")
        return False


def test_environment():
    """Test environment configuration."""
    print("\n🔐 Vault Keeper: Testing environment...")

    # Check required files
    required_files = [
        ".agent.yml",
        "fly.toml",
        "Dockerfile",
        "requirements.txt",
        "README_DEV.md",
        "xo_agents/web/__init__.py",
        "xo_agents/web/middleware.py",
        "xo_agents/web/tasks.py",
        "xo_agents/web/webhook_router.py",
        "xo_agents/api.py",
        ".github/workflows/webhook-trigger.yml",
    ]

    all_files_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}: Exists")
        else:
            print(f"❌ {file_path}: Missing")
            all_files_exist = False

    return all_files_exist


def test_fastapi_app():
    """Test FastAPI application."""
    print("\n🔐 Vault Keeper: Testing FastAPI application...")

    try:
        from xo_agents.api import app

        # Check if app has expected attributes
        if hasattr(app, "routes"):
            print(f"✅ FastAPI app has {len(app.routes)} routes")
        else:
            print("❌ FastAPI app missing routes")
            return False

        # Check if middleware is configured
        if hasattr(app, "user_middleware"):
            print(f"✅ FastAPI app has {len(app.user_middleware)} middleware")
        else:
            print("❌ FastAPI app missing middleware")
            return False

        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🔐 Vault Keeper: Starting XO Agent system tests...")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Task Registry", test_task_registry),
        ("Webhook Endpoints", test_webhook_endpoints),
        ("Environment", test_environment),
        ("FastAPI App", test_fastapi_app),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("🔐 Vault Keeper: Test Results Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! XO Agent system is ready for deployment!")
        print("🔐 Vault Keeper: Digital essence preserved and validated!")
        return True
    else:
        print("❌ Some tests failed! Please fix issues before deployment.")
        print(
            "🔐 Vault Keeper: Digital essence compromised - manual intervention required!"
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

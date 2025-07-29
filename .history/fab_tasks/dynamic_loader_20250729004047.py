from invoke import Collection, task
import os
import importlib
import inspect
from pathlib import Path

# Import local modules
from src.xo_core.fab_tasks.dns_check_21xo import check_dns
from src.xo_core.fab_tasks.deploy import test_deploy


@task
def discover_tasks(c, path="src/xo_core/fab_tasks", verbose=False):
    """
    Dynamically discover and load all available tasks from src.xo_core.fab_tasks.

    Args:
        path (str): Path to search for task modules
        verbose (bool): Show detailed discovery information
    """
    print(f"🔍 Discovering tasks in {path}")

    if not os.path.exists(path):
        print(f"❌ Path not found: {path}")
        return

    discovered_tasks = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Skip directories and non-Python files
        if os.path.isdir(item_path) or not item.endswith(".py"):
            continue

        module_name = item[:-3]  # Remove .py extension

        try:
            # Import the module
            module_path = f"src.xo_core.fab_tasks.{module_name}"
            module = importlib.import_module(module_path)

            # Find tasks in the module
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, "__wrapped__") and hasattr(obj.__wrapped__, "task"):
                    discovered_tasks.append(f"{module_name}.{name}")
                    if verbose:
                        print(f"  ✅ Found task: {module_name}.{name}")

        except ImportError as e:
            if verbose:
                print(f"  ⚠️ Could not import {module_name}: {e}")

    print(f"📋 Discovered {len(discovered_tasks)} tasks")
    return discovered_tasks


@task
def load_namespace(c, namespace="all"):
    """
    Load a specific namespace of tasks.

    Args:
        namespace (str): Namespace to load (dns, deploy, vault, pulse, etc.)
    """
    print(f"📦 Loading namespace: {namespace}")

    namespace_modules = {
        "dns": ["dns_check_21xo"],
        "deploy": ["deploy"],
        "vault": ["vault_tasks"],
        "pulse": ["pulse_tasks"],
        "drops": ["drop_tasks"],
        "digest": ["digest_tasks"],
        "summary": ["summary_tasks"],
        "all": [
            "dns_check_21xo",
            "deploy",
            "vault_tasks",
            "pulse_tasks",
            "drop_tasks",
            "digest_tasks",
            "summary_tasks",
        ],
    }

    if namespace not in namespace_modules:
        print(f"❌ Unknown namespace: {namespace}")
        print(f"Available: {list(namespace_modules.keys())}")
        return

    modules = namespace_modules[namespace]
    loaded_collections = []

    for module_name in modules:
        try:
            module = importlib.import_module(f"src.xo_core.fab_tasks.{module_name}")
            collection = Collection.from_module(module)
            loaded_collections.append((module_name, collection))
            print(f"  ✅ Loaded: {module_name}")
        except ImportError as e:
            print(f"  ❌ Failed to load {module_name}: {e}")

    return loaded_collections


@task
def list_available(c):
    """
    List all available task namespaces and modules.
    """
    print("📋 Available XO Core Task Namespaces:")
    print("  🌐 dns      - DNS management and validation")
    print("  🚀 deploy   - Deployment automation")
    print("  🔐 vault    - Vault service tasks")
    print("  ⚡ pulse    - Pulse service tasks")
    print("  📦 drops    - Drop management")
    print("  📰 digest   - Digest generation")
    print("  📊 summary  - System summaries")
    print("  🌟 all      - Load all namespaces")


# Create namespace
ns = Collection("loader")
ns.add_task(discover_tasks, "discover")
ns.add_task(load_namespace, "load")
ns.add_task(list_available, "list")

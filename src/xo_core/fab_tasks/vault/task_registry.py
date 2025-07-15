"""
Universal Task Registry for XO Vault Plug-ins

This module provides a clean way to discover and register tasks from vault modules
without causing recursion or namespace conflicts.
"""

from invoke import Collection
from pathlib import Path
from importlib import import_module
import logging

logger = logging.getLogger(__name__)

def load_vault_tasks(vault_ns: Collection, base_path: str = "xo_core.fab_tasks.vault", 
                    exclude_files: set = None) -> None:
    """
    Auto-register all vault/*.py modules except excluded ones.
    
    Args:
        vault_ns: The vault namespace collection to add tasks to
        base_path: The Python import path for vault modules
        exclude_files: Set of filenames to exclude (without .py extension)
    """
    if exclude_files is None:
        exclude_files = {"__init__", "utils", "internal", "task_registry"}
    
    vault_path = Path("src/xo_core/fab_tasks/vault")
    
    for file in vault_path.glob("*.py"):
        name = file.stem
        if name in exclude_files:
            continue
            
        try:
            module = import_module(f"{base_path}.{name}")
            
            # Check if module has a namespace
            if hasattr(module, "ns"):
                logger.info(f"📦 Adding vault module: {name}")
                vault_ns.add_collection(module.ns, name=name)
            # Check if module has individual tasks
            elif hasattr(module, "__all__"):
                for task_name in module.__all__:
                    if hasattr(module, task_name):
                        task = getattr(module, task_name)
                        if hasattr(task, "__wrapped__"):  # Check if it's a task
                            logger.info(f"📦 Adding vault task: {name}.{task_name}")
                            vault_ns.add_task(task, name=f"{name}-{task_name}")
                            
        except ImportError as e:
            logger.warning(f"⚠️ Failed to import vault module {name}: {e}")
        except Exception as e:
            logger.error(f"❌ Error loading vault module {name}: {e}")

def register_selected_tasks(module, task_names: list, namespace: Collection, 
                          prefix: str = "") -> None:
    """
    Register only specific tasks from a module.
    
    Args:
        module: The module containing the tasks
        task_names: List of task function names to register
        namespace: The collection to add tasks to
        prefix: Optional prefix for task names
    """
    for task_name in task_names:
        if hasattr(module, task_name):
            task = getattr(module, task_name)
            if hasattr(task, "__wrapped__"):  # Check if it's a task
                full_name = f"{prefix}{task_name}" if prefix else task_name
                logger.info(f"📦 Adding selected task: {full_name}")
                namespace.add_task(task, name=full_name)
            else:
                logger.warning(f"⚠️ {task_name} is not a task function")
        else:
            logger.warning(f"⚠️ Task {task_name} not found in module")

def create_vault_namespace() -> Collection:
    """
    Create a clean vault namespace with auto-discovered tasks.
    
    Returns:
        Collection: The vault namespace with all discovered tasks
    """
    vault_ns = Collection("vault")
    
    # Auto-discover vault modules
    load_vault_tasks(vault_ns)
    
    return vault_ns

# Example usage:
# vault_ns = create_vault_namespace()
# ns.add_collection(vault_ns, name="vault") 
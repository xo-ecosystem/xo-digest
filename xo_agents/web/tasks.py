"""
XO Agents Web Tasks

Task execution logic for webhook-triggered operations.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

fab_tasks_base = "xo_core.fab_tasks"

logger = logging.getLogger(__name__)


# 🔐 Vault Keeper: Central task registry for digital essence operations
SUPPORTED_TASKS = {
    "pulse.sync": {
        "description": "🔐 Sync pulse bundle to production with Vault Keeper precision",
        "args": ["bundle_name"],
        "module": "xo_core.fab_tasks.vault_pulse_sync",
        "function": "sync",
    },
    "vault.sign-all": {
        "description": "🔐 Sign all vault personas with sacred duty",
        "args": [],
        "module": "xo_core.fab_tasks.vault_tasks",
        "function": "sign_all",
    },
    "vault.bundle": {
        "description": "🔐 Create vault bundle for digital essence preservation",
        "args": ["bundle_name"],
        "module": "xo_core.fab_tasks.vault_tasks",
        "function": "bundle",
    },
    "agent.dispatch": {
        "description": "🔐 Dispatch agent persona with autonomous precision",
        "args": ["persona", "webhook", "preview", "memory"],
        "module": "shared.agent_logic",
        "function": "dispatch_persona",
    },
    "patch.apply": {
        "description": "🔐 Apply patch bundle with modular grace",
        "args": ["bundle_path"],
        "module": "fab_tasks.patch",
        "function": "apply",
    },
    "dns.check": {
        "description": "🔐 Check DNS records for cosmic alignment",
        "args": ["dry_run"],
        "module": "fab_tasks.dns_check_21xo",
        "function": "check_dns",
    },
    "deploy.test": {
        "description": "🔐 Test deployment with production readiness",
        "args": ["service", "endpoint"],
        "module": "fab_tasks.deploy",
        "function": "test_deploy",
    },
    "cosmic.align": {
        "description": "🔐 Full cosmic alignment with system harmony",
        "args": ["dry_run"],
        "module": "fabfile",
        "function": "cosmic_align",
    },
    "dashboard.sync": {
        "description": "🔐 Sync dashboard artifacts with precision",
        "args": [],
        "module": "fabfile",
        "function": "dashboard_sync",
    },
}


class TaskRequest(BaseModel):
    """Task request model for webhook payloads."""

    task: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}


class TaskResponse(BaseModel):
    """Task response model."""

    status: str
    task: str
    result: Optional[Any] = None
    error: Optional[str] = None


def run_task(
    task: str, args: List[Any] = None, kwargs: Dict[str, Any] = None
) -> TaskResponse:
    """
    Execute a task with detailed logging and validation.

    Args:
        task: Task name to execute
        args: Positional arguments for the task
        kwargs: Keyword arguments for the task

    Returns:
        TaskResponse with execution result
    """
    args = args or []
    kwargs = kwargs or {}

    logger.info(
        f"🔐 Vault Keeper: Executing task '{task}' with args={args}, kwargs={kwargs}"
    )

    # Validate task exists
    if task not in SUPPORTED_TASKS:
        error_msg = f"🔐 Vault Keeper: Unknown task '{task}'. Supported tasks: {list(SUPPORTED_TASKS.keys())}"
        logger.error(error_msg)
        return TaskResponse(status="error", task=task, error=error_msg)

    task_config = SUPPORTED_TASKS[task]
    logger.info(
        f"🔐 Vault Keeper: Task configuration loaded - {task_config['description']}"
    )

    try:
        # Import the module dynamically
        import importlib

        module_path = task_config["module"]
        module = importlib.import_module(module_path)
        function = getattr(module, task_config["function"])

        logger.info(
            f"🔐 Vault Keeper: Successfully imported {module_path}.{task_config['function']}"
        )

        # Execute the task
        if kwargs:
            result = function(*args, **kwargs)
        else:
            result = function(*args)

        logger.info(f"🔐 Vault Keeper: Task '{task}' completed with precision")

        return TaskResponse(status="success", task=task, result=result)

    except ImportError as e:
        error_msg = f"🔐 Vault Keeper: Failed to import module {module_path}: {e}"
        logger.error(error_msg)
        return TaskResponse(status="error", task=task, error=error_msg)
    except AttributeError as e:
        error_msg = f"🔐 Vault Keeper: Function {task_config['function']} not found in {module_path}: {e}"
        logger.error(error_msg)
        return TaskResponse(status="error", task=task, error=error_msg)
    except Exception as e:
        error_msg = (
            f"🔐 Vault Keeper: Task '{task}' failed - digital essence compromised: {e}"
        )
        logger.error(error_msg)
        return TaskResponse(status="error", task=task, error=error_msg)


def get_available_tasks() -> Dict[str, Dict[str, Any]]:
    """Get list of available tasks with descriptions."""
    return SUPPORTED_TASKS


def validate_task_request(task: str, args: List[Any] = None) -> bool:
    """Validate that a task request is valid."""
    if task not in SUPPORTED_TASKS:
        return False

    task_config = SUPPORTED_TASKS[task]
    expected_args = task_config.get("args", [])

    # Basic validation - could be enhanced
    if args and len(args) > len(expected_args):
        logger.warning(f"Task {task} received more args than expected")

    return True

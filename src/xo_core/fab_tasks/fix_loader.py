# src/xo_core/fab_tasks/fix_loader.py

import importlib
import logging
import os
from pathlib import Path
from invoke import Collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fab_loader")


def run_safe_loader():
    ns = Collection()
    task_dir = Path(__file__).parent
    task_files = [
        f
        for f in task_dir.glob("*.py")
        if f.name not in {"__init__.py", "fix_loader.py"}
    ]

    for task_file in task_files:
        module_name = f"xo_core.fab_tasks.{task_file.stem}"
        try:
            mod = importlib.import_module(module_name)
            if hasattr(mod, "ns"):
                ns.add_collection(mod.ns, name=task_file.stem)
                logger.info(f"✅ Loaded: {module_name}")
            else:
                logger.warning(f"⚠️ No namespace found in {module_name}")
        except Exception as e:
            logger.warning(f"❌ Failed to load {module_name}: {e}")

    return ns

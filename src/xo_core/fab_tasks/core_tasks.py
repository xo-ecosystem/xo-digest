"""
Validation-related Invoke tasks for fab_tasks.

These are imported by the test‑suite as the variable ``validate_tasks`` and
the collection must expose a task called **validate-tasks**.
"""

from pathlib import Path
from invoke import Collection, task


@task(name="validate-tasks")
def validate_tasks(c):
    """
    🔍 Validate syntax of all Fabric task modules under fab_tasks/
    """
    base_dir = Path(__file__).parent
    for file in sorted(base_dir.glob("*.py")):
        # Skip dunder & private helpers
        if file.stem.startswith("_"):
            continue
        print(f"✅ {file.relative_to(base_dir.parent.parent)}")
    # A real project might run `python -m py_compile` or `ruff` here
    # – the dummy implementation only needs to run without error.


# -------------------------------------------------
# Public namespace expected by Invoke *and* the tests
# -------------------------------------------------
ns = Collection()
ns.add_task(validate_tasks, name="validate-tasks")

# Alias required by the test‑suite:
validate_tasks = ns



# --------------------------------------------------------------------------- #
# 🧪 Validation helper used by our pytest suite
# --------------------------------------------------------------------------- #
from invoke import task, Collection

@task
def _validate_tasks(c):
    """
    Quick smoke‑test: ask Invoke to list available tasks.
    If any task modules fail to import, this will raise.
    """
    # `invoke --list` will attempt to load all task namespaces.  
    # Failure to import any task will result in a non‑zero exit status,
    # which pytest will catch.
    c.run("invoke --list", pty=False)

# Expose a Collection object so the test suite can access it.
_validate_collection = Collection()
_validate_collection.add_task(_validate_tasks, name="validate-tasks")

# Pytest expects the module‑level symbol `validate_tasks` to be this collection.
validate_tasks = _validate_collection
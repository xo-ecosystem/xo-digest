"""
Fabric tasks validation module.
"""

from invoke import Collection, Context, task

from .pulse_namespace import pulse_ns
from .validate_tasks import validate_tasks as _validate_tasks_task

# A collection that exposes the single "validate-tasks" Invoke task.
# The tests expect to access it via:  validate_tasks["validate-tasks"]
validate_tasks = Collection("validate_tasks")
# Register the task and make it the *default* for this collection so that
# calling the collection itself (or leaving a blank task name) still
# resolves to the same callable.  This matches what the unit‑tests expect.
validate_tasks.add_task(_validate_tasks_task, name="validate-tasks", default=True)

# ------------------------------------------------------------------
# Root collection that aggregates all fab sub‑namespaces and tasks.
# ------------------------------------------------------------------
tasks = Collection("tasks")
tasks.add_collection(pulse_ns)
tasks.add_collection(validate_tasks)

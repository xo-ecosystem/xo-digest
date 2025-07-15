"""Root Fabric tasks collection and validation setup."""

from invoke import Collection

# Aggregate all task namespaces under the root `tasks` collection
tasks = Collection("tasks")

# Import and add summary tasks to the main collection
def add_summary_tasks():
    from .summary_tasks import ns as summary_ns
    tasks.add_collection(summary_ns)

# Import sub-namespaces and default tasks
from .pulse_namespace import pulse_ns
from .pulse.preview import export_html
from .pulse.publish import publish
from .validate_tasks import validate_tasks as _validate_tasks_task

pulse_ns.add_task(export_html, name="export-html")
pulse_ns.add_task(publish, name="publish")

# A collection that exposes the single "validate-tasks" Invoke task.
# The tests expect to access it via:  validate_tasks["validate-tasks"]
validate_tasks = Collection("validate_tasks")
validate_tasks.add_task(_validate_tasks_task, name="validate-tasks", default=True)

tasks.add_collection(pulse_ns)
tasks.add_collection(validate_tasks)
add_summary_tasks()

# This module exposes the full task tree for use in `fabfile.py`

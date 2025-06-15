from .pulse_namespace import pulse_ns
from .validate_tasks import validate_tasks as validate_task_fn
from .core_tasks import validate_tasks as validate_core_tasks

tasks = Collection("tasks")
tasks.add_task(validate_task_fn)
tasks.add_task(validate_core_tasks)
tasks.add_collection(pulse_ns)

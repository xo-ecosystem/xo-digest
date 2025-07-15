from invoke import Collection
from .core_tasks import validate_tasks as validate_core_tasks
from .pulse import ns as pulse
from .pulse_namespace import pulse_ns as pulse_namespace
from .validate_tasks import validate_tasks as validate_task_fn

ns = Collection()
ns.add_collection(validate_task_fn)
ns.add_collection(validate_core_tasks)
ns.add_collection(pulse_namespace)
ns.add_collection(pulse)

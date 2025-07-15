from .core_tasks import validate_tasks as validate_core_tasks
from .pulse_namespace import pulse_ns as pulse_namespace
from .validate_tasks import validate_tasks as validate_task_fn
from .pulse import ns as pulse

ns = Collection()
ns.add_task(validate_task_fn)
ns.add_task(validate_core_tasks)
ns.add_collection(pulse_namespace)
ns.add_collection(pulse)

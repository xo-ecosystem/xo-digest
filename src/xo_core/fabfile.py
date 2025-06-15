from invoke import Collection

from xo_core.fab_tasks import drop_tasks
from xo_core.pulse_tasks import ns as pulse_ns

root = Collection()
root.add_collection(pulse_ns, name="pulse")

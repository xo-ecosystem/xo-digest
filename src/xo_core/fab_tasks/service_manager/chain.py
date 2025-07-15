

from invoke import Collection
from xo_core.fab_tasks.service_manager import service_manager

ns = Collection("service-manager")
ns.add_collection(service_manager.ns, name="service")
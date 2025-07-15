from invoke import Collection
from xo_core.fab_tasks import core_tasks, pulse_namespace, digest_tasks

def all_registered_tasks():
    """
    Return a list of all registered tasks for summary generation.
    Safely handles namespaces without a `.tasks` attribute.
    """
    tasks = []
    for ns in [core_tasks, pulse_namespace, digest_tasks]:
        if hasattr(ns, "tasks"):
            tasks.extend(ns.tasks.values())
    return tasks
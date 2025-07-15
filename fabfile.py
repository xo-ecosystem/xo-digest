from invoke import Collection
from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader

root = Collection()
loader = DynamicTaskLoader()

for name, namespace in loader.discover_namespaces().items():
    root.add_collection(namespace, name=name)

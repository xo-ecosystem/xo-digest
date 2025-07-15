# test_loader.py
from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader

loader = DynamicTaskLoader()
namespaces = loader.discover_namespaces()

for name, ns in namespaces.items():
    print(f"✅ Loaded namespace: {name} ({type(ns)})")
from xo_core.fab_tasks.dynamic_loader import DynamicTaskLoader

def get_discovered_namespaces():
    loader = DynamicTaskLoader()
    return loader.discover_namespaces()

def test_discovery_not_crashing():
    namespaces = get_discovered_namespaces()
    assert isinstance(namespaces, dict)
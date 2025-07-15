# scripts/debug_namespace.py
from invoke import Collection
from xo_core.fab_tasks import pulse_tasks  # or any known stable module

def check_namespace(ns, seen=None, depth=0):
    seen = seen or set()
    if id(ns) in seen:
        print("⚠️ Circular ref found at depth", depth)
        return
    seen.add(id(ns))
    print("📁", "  " * depth, ns.name or "<root>", f"({len(ns.tasks)} tasks)")
    for _, sub_ns in ns.collections.items():
        check_namespace(sub_ns, seen, depth + 1)

if __name__ == "__main__":
    ns = Collection()
    ns.add_collection(pulse_tasks.ns)  # Replace with the suspected one
    check_namespace(ns)

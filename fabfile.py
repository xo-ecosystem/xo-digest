from invoke import Collection, task

print("🔧 Loading fabfile.py...")

# Create main namespace
ns = Collection()

@task
def test(c):
    """Test task to verify fabfile works"""
    print("✅ Fabfile is working!")

ns.add_task(test)

def safe_add_collection(module_path, collection_name, namespace_name=None):
    """Safely add a collection with error handling"""
    try:
        module = __import__(module_path, fromlist=[''])
        if hasattr(module, collection_name):
            collection = getattr(module, collection_name)
            ns.add_collection(collection, name=namespace_name or collection_name.lower().replace('_ns', ''))
            print(f"✅ Added {namespace_name or collection_name.lower().replace('_ns', '')} collection")
            return True
        else:
            print(f"⚠️ {module_path} has no {collection_name} - skipping")
            return False
    except ImportError as e:
        print(f"⚠️ {module_path} not available - skipping import: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error loading {module_path}: {e}")
        return False

# Add all task modules
collections_to_try = [
    ("xo_core.fab_tasks.env_tasks", "env_ns", "env"),
    ("xo_core.fab_tasks.storage_tasks", "storage_ns", "storage"),
    ("xo_core.fab_tasks.backend_tasks", "backend_ns", "backend"),
    ("xo_core.fab_tasks.sign_tasks", "sign_ns", "sign"),
    ("xo_core.fab_tasks.seal_tasks", "seal_ns", "seal"),
    ("xo_core.fab_tasks.cosmos_tasks", "cosmos_ns", "cosmos"),
    ("xo_core.fab_tasks.spec_sync", "spec_ns", "spec"),
    ("xo_core.fab_tasks.vault", "vault_ns", "vault"),
    ("xo_core.fab_tasks.pulse_namespace", "pulse_ns", "pulse"),
    ("xo_core.fab_tasks.inbox", "notify_ns", "notify"),
]

for module_path, collection_name, namespace_name in collections_to_try:
    safe_add_collection(module_path, collection_name, namespace_name)

# Configure the namespace
ns.configure({
    'run': {'echo': True}
})

# Define the default namespace (required for Fabric)
namespace = ns

print("✅ fabfile.py loaded successfully!")
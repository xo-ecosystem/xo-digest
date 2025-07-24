import logging
from invoke import Collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create main namespace
ns = Collection()

def safe_add_collection(module_path, collection_name, namespace_name=None):
    """Safely add a collection with error handling"""
    try:
        module = __import__(module_path, fromlist=[''])
        if hasattr(module, collection_name):
            collection = getattr(module, collection_name)
            ns.add_collection(collection, name=namespace_name or collection_name.lower().replace('_ns', ''))
            logger.info(f"✅ Added {namespace_name or collection_name.lower().replace('_ns', '')} collection")
            return True
        else:
            logger.warning(f"⚠️ {module_path} has no {collection_name} - skipping")
            return False
    except ImportError as e:
        logger.warning(f"⚠️ {module_path} not available - skipping import: {e}")
        return False
    except Exception as e:
        logger.warning(f"⚠️ Error loading {module_path}: {e}")
        return False

# Core task namespaces - only add what we know works
collections_to_try = [
    ("xo_core.fab_tasks.env_tasks", "env_ns", "env"),
    ("xo_core.fab_tasks.storage_tasks", "storage_ns", "storage"),
    ("xo_core.fab_tasks.backend_tasks", "backend_ns", "backend"),
    ("xo_core.fab_tasks.sign_tasks", "sign_ns", "sign"),
    ("xo_core.fab_tasks.seal_tasks", "seal_ns", "seal"),
    ("xo_core.fab_tasks.cosmos_tasks", "cosmos_ns", "cosmos"),
    ("xo_core.fab_tasks.spec_sync", "spec_ns", "spec"),
    ("xo_core.fab_tasks.dev_doctor_tasks", "ns", "dev"),
    # Temporarily disabled to isolate vault-agent issue
    # ("xo_core.fab_tasks.fabfile_health", "health_ns", "health"),
]

# Add collections safely
for module_path, collection_name, namespace_name in collections_to_try:
    safe_add_collection(module_path, collection_name, namespace_name)

# Configure the namespace
ns.configure({
    'run': {'echo': True}
})

# Define the default namespace (required for Fabric)
namespace = ns
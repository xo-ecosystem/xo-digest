from invoke import task, Collection

# Create main namespace
ns = Collection()

# Add drop_patch tasks
try:
    from xo_core.fab_tasks.drop_patch import ns as drop_patch_ns
    ns.add_collection(drop_patch_ns, name="drop")
    print("✅ Drop namespace added successfully")
except ImportError as e:
    print(f"❌ Drop namespace not loaded: {e}")

# Add preview tasks
try:
    from xo_core.fab_tasks.preview import ns as preview_ns
    ns.add_collection(preview_ns, name="preview")
    print("✅ Preview namespace added successfully")
except ImportError as e:
    print(f"❌ Preview namespace not loaded: {e}")

# Define the default namespace
namespace = ns 
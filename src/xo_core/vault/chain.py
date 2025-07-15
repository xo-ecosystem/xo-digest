from invoke import Collection
from xo_core.fab_tasks.vault import digest

ns = Collection("vault")
ns.add_collection(digest.ns, name="digest")
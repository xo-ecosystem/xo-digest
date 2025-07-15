from invoke import Collection
from xo_core.fab_tasks.tunnel import fabfile

ns = Collection("tunnel")
ns.add_collection(fabfile.ns, name="fabfile")

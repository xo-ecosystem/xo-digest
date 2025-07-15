from invoke import Collection
from xo_core.fab_tasks.inbox.all_with_link import ns as all_with_link_ns

ns = Collection("inbox")
ns.add_collection(all_with_link_ns, name="all-with-link")

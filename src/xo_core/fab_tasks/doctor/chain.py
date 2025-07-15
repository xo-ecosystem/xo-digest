from invoke import Collection
from xo_core.fab_tasks.doctor import report

ns = Collection("doctor")
ns.add_collection(report.ns, name="report")

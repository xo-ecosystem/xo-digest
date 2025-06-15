from invoke import Collection

from xo_core.agent0.tasks import ns as agent0_ns
from xo_core.fab_tasks import tasks as fab_tasks
from xo_core.xo_agent.tasks import ns as xo_agent_ns

ns = Collection()
ns.add_collection(fab_tasks, name="fab")
ns.add_collection(agent0_ns, name="agent0")
ns.add_collection(xo_agent_ns, name="xo_agent")

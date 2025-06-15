# src/xo_core/agents/__init__.py
from invoke import Collection

from xo_core.agent0.tasks import ns as agent0_ns
from xo_core.xo_agent.tasks import ns as xo_agent_ns

namespace = Collection("agents")
namespace.add_collection(agent0_ns)
namespace.add_collection(xo_agent_ns)

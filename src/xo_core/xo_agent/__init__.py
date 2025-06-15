"""XO Agent module – manages persona deployment and reload tasks."""

from invoke import Collection

from xo_core.agent0.tasks import ns as agent0_ns

from .tasks import ns as xo_agent_ns

# Expose the agent task namespace for Invoke
namespace = Collection("xo_agent")
namespace.add_collection(xo_agent_ns)

__all__ = ["namespace"]

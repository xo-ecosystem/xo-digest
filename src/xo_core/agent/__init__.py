#
#   Init   Module
#   src/xo_core/agent/__init__.py
#   Namespace: agent

from invoke import Collection

from xo_core.agent0.tasks import ns as agent0_ns
from xo_core.xo_agent.tasks import ns as xo_agent_ns

namespace = Collection("agent")
namespace.add_collection(agent0_ns)
namespace.add_collection(xo_agent_ns)

from xo_core.agent.agent_game import AgentGame
from xo_core.agent.agent_persona import AgentPersona
from xo_core.agent.agent_api import agent_api as AgentAPI
from xo_core.agent.agent_hooks import AgentHooks

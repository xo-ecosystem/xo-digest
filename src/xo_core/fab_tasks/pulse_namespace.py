# src/xo_core/fab_tasks/pulse_namespace.py
from invoke import Collection

from . import pulse_tasks

"""
📦 Pulse Namespace

Collection of Fabric tasks related to managing and syncing Pulse entries,
including creation, archiving, and synchronization across environments.
"""
pulse_ns = Collection("pulse")
pulse_ns.doc = "📦 Pulse-related tasks for managing and syncing pulse entries."
pulse_tasks.sync.__doc__ = "🔄 Sync pulses."
pulse_ns.add_task(
    pulse_tasks.sync,
    "sync"
)
# ...other tasks

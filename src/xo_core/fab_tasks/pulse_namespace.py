# src/xo_core/fab_tasks/pulse_namespace.py
from invoke import Collection

from . import pulse_tasks

pulse_ns = Collection("pulse")
pulse_ns.add_task(pulse_tasks.sync, "sync")
# ...other tasks

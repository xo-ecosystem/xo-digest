from invoke import Collection

from . import pulse

ns = Collection("pulse")
ns.add_task(pulse.sync, name="sync")
ns.add_task(pulse.sign, name="sign")

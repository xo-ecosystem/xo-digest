from invoke import Collection

from . import cursor, doctor
from .pulse import ns as pulse_ns

ns = Collection()
ns.add_collection(Collection.from_module(cursor), name="cursor")
ns.add_collection(Collection.from_module(doctor), name="doctor")
ns.add_collection(Collection.from_module(pulse), name="pulse")

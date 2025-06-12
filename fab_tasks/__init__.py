from invoke import Collection

from .pulse import ns as pulse_ns

ns = Collection()
ns.add_collection(pulse_ns)

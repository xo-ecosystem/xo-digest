from invoke import Collection

try:
    from . import cosmic

    ns = Collection("cosmic")
    ns.add_collection(cosmic.ns, name="cosmic")
except ImportError:
    ns = Collection("cosmic")

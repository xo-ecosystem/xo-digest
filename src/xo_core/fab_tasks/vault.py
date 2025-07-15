from invoke import Collection

from . import chain, digest, sign, bundle, preview, verify

ns = Collection("vault")
for mod in (chain, digest, sign, bundle, preview, verify):
    ns.add_collection(Collection.from_module(mod), name=mod.__name__)
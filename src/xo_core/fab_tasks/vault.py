from invoke import Collection

from . import chain, digest, sign, bundle, preview, verify
from . import vault_tasks as vault

ns = Collection("vault")
import sys

sys.modules["fab_tasks.vault"] = sys.modules[__name__]
for mod in (chain, digest, sign, bundle, preview, verify):
    ns.add_collection(Collection.from_module(mod), name=mod.__name__)

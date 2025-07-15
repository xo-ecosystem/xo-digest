from invoke import Collection

try:
    from . import api_utils

    ns = Collection("cloudflare-utils")
    ns.add_collection(api_utils.ns, name="api-utils")
except ImportError:
    ns = Collection("cloudflare-utils")

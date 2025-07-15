try:
    from xo_core.fab_tasks.digest import ns as digest_ns
    ns.add_collection(digest_ns)
except ImportError as e:
    if "partially initialized module" in str(e):
        import warnings
        warnings.warn("Skipped digest_ns import due to circular import.")
    else:
        raise
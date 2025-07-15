from invoke import task, Collection

@task
def open(c, slug):
    """
    👁️ Open pulse in browser preview (uses localhost preview server).
    """
    import webbrowser

    webbrowser.open(f"http://localhost:8787/pulse/{slug}")


# Create namespace
ns = Collection("open")
ns.add_task(open)

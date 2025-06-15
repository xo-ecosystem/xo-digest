from invoke import Collection, task


@task
def new(c, slug):
    """Create a new pulse task."""
    pass


@task
def sync(c):
    """Sync pulse tasks."""
    pass


@task
def archive_all(c):
    """Archive all pulse tasks."""
    pass


ns = Collection("pulse")
ns.add_task(new, name="new")
ns.add_task(sync, name="sync")
ns.add_task(archive_all, name="archive-all")

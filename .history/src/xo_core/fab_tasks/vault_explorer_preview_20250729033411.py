from invoke import task, Collection

ns = Collection()


@task
def pulse_sync(ctx):
    # placeholder logic
    print("Syncing pulse...")


ns.add_task(pulse_sync)

explorer_preview = ns

from invoke import task, Collection

@task
def ping(ctx):
    print("Pinging Cloudflare...")

ns = Collection()
ns.add_task(ping)

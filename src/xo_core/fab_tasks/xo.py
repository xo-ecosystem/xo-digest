from invoke import task


@task
def drops_ci(c):
    c.run("make xo-drops-ci")


from invoke import Collection

ns = Collection("xo")
ns.add_task(drops_ci)

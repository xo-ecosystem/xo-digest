from invoke import task

@task
def dev(c):
    with c.cd("src/xo_core/web"):
        c.run("npm run dev", pty=True)

@task
def build(c):
    with c.cd("src/xo_core/web"):
        c.run("npm run build", pty=True)

@task
def install(c):
    with c.cd("src/xo_core/web"):
        c.run("npm install", pty=True)

from invoke import task, Collection

@task
def bundle_all(c):
    print("📦 Bundling vault content...")

ns = Collection("bundle")
ns.add_task(bundle_all, name="all")

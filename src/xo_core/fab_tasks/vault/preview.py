
from invoke import task, Collection

@task
def preview_all(c):
    print("🧪 Generating all vault previews...")

ns = Collection("preview")
ns.add_task(preview_all, name="all")

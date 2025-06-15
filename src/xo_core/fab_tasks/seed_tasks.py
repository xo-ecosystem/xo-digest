from invoke import Collection, task


@task(help={"seed_file": "Path to the .yml file"})
def submit(c, seed_file):
    print(f"📥 Submitting seed: {seed_file}")
    # Insert logic here


@task(help={"seed_file": "Path to the .yml file"})
def drop(c, seed_file):
    print(f"🗑️ Dropping seed: {seed_file}")
    # Insert logic here


@task
def drop_all(c):
    print("🧹 Dropping all seeds from ./seeds/")
    # Insert logic here


ns = Collection("seed")
ns.add_task(submit)
ns.add_task(drop)
ns.add_task(drop_all, name="drop-all")

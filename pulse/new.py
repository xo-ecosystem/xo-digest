from invoke import task, Collection

@task
def eighth_seal(c):
    print("✅ Created eighth seal pulse")

ns = Collection("new")
ns.add_task(eighth_seal, name="eighth_seal")
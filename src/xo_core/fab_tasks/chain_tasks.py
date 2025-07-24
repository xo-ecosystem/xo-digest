from invoke import Collection, task

@task
def constellation_unfold(c):
    print("✨ Unfolding constellation logic...")

ns = Collection("chain")
ns.add_task(constellation_unfold, name="constellation_unfold")

@task
def execute_sequence(c):
    c.run("xo-fab chain.constellation_unfold")
    c.run("xo-fab pitchdeck.dropper")
    c.run("xo-fab cosmos.initiate_loop")

ns.add_task(execute_sequence, name="execute_sequence")



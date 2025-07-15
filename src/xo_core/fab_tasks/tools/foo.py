from invoke import task, Collection

@task
def example(ctx):
    print("This is a sample task.")

ns = Collection("tools.foo")
ns.add_task(example)

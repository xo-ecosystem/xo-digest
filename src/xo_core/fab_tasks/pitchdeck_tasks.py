from invoke import Collection, task

@task
def dropper(c):
    print("📤 Pitchdeck drop deployed!")

ns = Collection("pitchdeck")
ns.add_task(dropper)
__all__ = ["ns"]
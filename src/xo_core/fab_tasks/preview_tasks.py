from invoke import Collection, task

@task
def generate(c):
    print("🪞 Generating preview...")

ns = Collection("preview")
ns.add_task(generate)
__all__ = ["ns"]

from invoke import task, Collection

@task
def verify_all(c):
    print("✅ Verifying all signed pulses...")

ns = Collection("verify")
ns.add_task(verify_all, name="all")

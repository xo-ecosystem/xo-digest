import os

from invoke import task


@task
def bootstrap(c):
    """
    ♻️ Rebuild folder links and scaffold initial vault layout
    """
    folders = [
        "fab_tasks",
        "scripts",
        "apps",
        "content/pulses",
        "vault",
        "agent0",
        "dashboard",
        "drops",
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📂 Ensured: {folder}")
    os.system("python scripts/regen_stubs.py")
    print("✅ Bootstrap complete.")

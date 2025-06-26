import os

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
    keep = os.path.join(folder, ".gitkeep")
    with open(keep, "w") as f:
        f.write("")
print("✅ Regen complete.")

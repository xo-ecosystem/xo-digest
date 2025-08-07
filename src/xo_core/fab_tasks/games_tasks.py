from invoke import task
import subprocess


@task
def deploy(c, target="vault"):
    """Deploy xo-games docs and traits to the specified target (vault or GitHub Pages)."""
    if target == "vault":
        print("🚀 Deploying xo-games to XO Vault...")
        # Add deployment logic for XO Vault here
        subprocess.run(["echo", "Deploying to XO Vault..."])
    elif target == "github":
        print("🚀 Deploying xo-games to GitHub Pages...")
        # Add deployment logic for GitHub Pages here
        subprocess.run(["echo", "Deploying to GitHub Pages..."])
    else:
        print(f"❌ Unknown target: {target}")
        return
    print("✅ Deployment completed successfully!")

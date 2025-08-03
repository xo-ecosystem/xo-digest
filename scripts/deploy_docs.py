#!/usr/bin/env python3
"""
Deploy xo-core-docs with GitHub App token.
Uses the docs.token functionality to deploy to GitHub Pages.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def deploy_docs():
    """Deploy docs to xo-core-docs repository using GitHub token."""
    print("📚 Deploying xo-core-docs with GitHub App token...")

    # Check if we have a token in .env.local
    dotenv_path = Path(".env.local")
    if not dotenv_path.exists():
        print(
            "❌ No .env.local found. Run 'python scripts/docs_token_direct.py' first."
        )
        return False

    # Read token from .env.local
    env_content = dotenv_path.read_text()
    gh_token = None
    for line in env_content.split("\n"):
        if line.startswith("GH_TOKEN="):
            gh_token = line.split("=", 1)[1].strip().strip("\"'")
            break

    if not gh_token:
        print(
            "❌ No GH_TOKEN found in .env.local. Run 'python scripts/docs_token_direct.py' first."
        )
        return False

    print(f"✅ Found GitHub token → {gh_token[:8]}...")

    # Check if mkdocs is available
    try:
        subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing mkdocs...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "mkdocs", "mkdocs-material"],
            check=True,
        )

    # Build docs
    print("🔨 Building documentation...")
    docs_dir = Path("xo-core-docs")
    if docs_dir.exists():
        os.chdir(docs_dir)
        try:
            subprocess.run(["mkdocs", "build"], check=True)
            print("✅ Documentation built successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build docs: {e}")
            return False

        # Deploy to GitHub Pages
        print("🚀 Deploying to GitHub Pages...")
        env = os.environ.copy()
        env["GH_TOKEN"] = gh_token

        try:
            result = subprocess.run(
                [
                    "mkdocs",
                    "gh-deploy",
                    "--force",
                    "--message",
                    "🔄 Auto-deploy from xo-core-dev",
                ],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            print("✅ Documentation deployed successfully!")
            print("📡 Available at: https://xo-ecosystem.github.io/xo-core-docs/")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to deploy docs: {e}")
            print(f"Error output: {e.stderr}")
            return False
    else:
        print("❌ xo-core-docs directory not found")
        return False


if __name__ == "__main__":
    # Change to repo root
    repo_root = Path(__file__).parent.parent
    os.chdir(repo_root)

    success = deploy_docs()
    sys.exit(0 if success else 1)

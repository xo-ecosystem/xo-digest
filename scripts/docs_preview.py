#!/usr/bin/env python3
"""
Launch a local preview server for XO Core docs.
Alternative to full deployment for development testing.
"""

import os
import sys
import subprocess
from pathlib import Path


def docs_preview():
    """Launch local docs preview server."""
    print("📚 Starting XO Core docs preview server...")

    # Change to docs directory
    docs_dir = Path("xo-core-docs")
    if not docs_dir.exists():
        print("❌ xo-core-docs directory not found")
        return False

    original_dir = os.getcwd()
    try:
        os.chdir(docs_dir)

        # Check if mkdocs is available
        try:
            subprocess.run(["mkdocs", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Installing mkdocs...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "mkdocs", "mkdocs-material"],
                check=True,
            )

        print("🚀 Starting local server at http://localhost:8000")
        print("💡 Press Ctrl+C to stop the server")

        # Start mkdocs serve
        subprocess.run(["mkdocs", "serve", "--dev-addr", "localhost:8000"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start docs server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n✅ Docs preview server stopped")
    finally:
        os.chdir(original_dir)

    return True


if __name__ == "__main__":
    success = docs_preview()
    sys.exit(0 if success else 1)

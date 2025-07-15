#!/usr/bin/env python3
"""
Pre-commit hook for XO Core Dev Doctor.
This script runs dev_doctor checks before commits to ensure code health.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_dev_doctor():
    """Run dev_doctor and return exit code."""
    try:
        # Get the project root (where fabfile.py is located)
        project_root = Path(__file__).parent.parent
        
        # Change to project root
        os.chdir(project_root)
        
        # Run dev_doctor
        result = subprocess.run([
            sys.executable, '-m', 'invoke', 'dev.doctor'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Dev Doctor check failed!")
            print(result.stdout)
            print(result.stderr)
            return result.returncode
        
        print("✅ Dev Doctor check passed!")
        print(result.stdout)
        return 0
        
    except Exception as e:
        print(f"❌ Error running Dev Doctor: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_dev_doctor()
    sys.exit(exit_code) 
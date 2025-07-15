#!/usr/bin/env python3
"""
Setup Cursor Integration for XO Fabric Tasks

This script sets up the complete Cursor integration including:
- Task index generation
- Agent configuration
- Task discovery tools
- Verification of chain files
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name: str, description: str) -> bool:
    """Run a script and return success status."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run([sys.executable, f"scripts/{script_name}"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        print(f"Stderr: {e.stderr}")
        return False


def check_files_exist() -> bool:
    """Check that required files exist."""
    required_files = [
        ".cursor/tasks.json",
        ".cursor/agents.json",
        "scripts/task_discovery.py",
        "scripts/generate_tasks_json.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up Cursor Integration for XO Fabric Tasks")
    print("=" * 60)
    
    # Step 1: Generate task index
    if not run_script("generate_tasks_json.py", "Generating task index"):
        print("❌ Failed to generate task index")
        return False
    
    # Step 2: Verify chain files
    if not run_script("verify_chain_files.py", "Verifying chain files"):
        print("⚠️ Chain file verification failed, but continuing...")
    
    # Step 3: Check required files
    if not check_files_exist():
        print("❌ Required files missing")
        return False
    
    # Step 4: Test task discovery
    print("\n🧪 Testing task discovery...")
    try:
        result = subprocess.run([sys.executable, "scripts/task_discovery.py", "summary"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Task discovery test failed: {e}")
        return False
    
    # Step 5: Show setup summary
    print("\n✅ Cursor Integration Setup Complete!")
    print("=" * 60)
    print("\n📋 Available Tools:")
    print("  • Task Discovery: python scripts/task_discovery.py")
    print("  • Task Index: .cursor/tasks.json")
    print("  • Agent Config: .cursor/agents.json")
    print("  • Auto-generation: python scripts/generate_tasks_json.py")
    
    print("\n🔍 Task Discovery Examples:")
    print("  • python scripts/task_discovery.py summary")
    print("  • python scripts/task_discovery.py search 'publish'")
    print("  • python scripts/task_discovery.py namespace pulse")
    print("  • python scripts/task_discovery.py category automation")
    print("  • python scripts/task_discovery.py workflow pulse-publishing")
    
    print("\n🎯 Cursor Agent Usage:")
    print("  • Use 'xo-fab-assistant' for general task help")
    print("  • Use 'xo-pulse-expert' for pulse content workflows")
    print("  • Use 'xo-vault-manager' for vault operations")
    print("  • Use 'xo-dev-tools' for development assistance")
    
    print("\n🔄 Maintenance:")
    print("  • Run 'python scripts/generate_tasks_json.py' after adding new tasks")
    print("  • Run 'python scripts/fix_fabric_tasks_simple.py' to fix task modules")
    print("  • Run 'python scripts/verify_chain_files.py' to check chain files")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
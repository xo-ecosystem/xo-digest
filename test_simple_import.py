#!/usr/bin/env python3
"""
Simple import test to isolate the 'function' object has no attribute 'aliases' error.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_import_sequence():
    """Test importing modules in sequence to find the problematic one."""
    
    modules_to_test = [
        "xo_core.fab_tasks.ipfs",
        "xo_core.fab_tasks.vault.digest", 
        "xo_core.fab_tasks.xo_collections",
        "xo_core.fab_tasks.validate_tasks",
        "xo_core.fab_tasks.core_tasks",
        "xo_core.fab_tasks.pulse.new",
        "xo_core.fab_tasks.pulse.sync",
        "xo_core.fab_tasks.pulse.archive",
    ]
    
    for module_name in modules_to_test:
        try:
            print(f"🔍 Testing import: {module_name}")
            module = __import__(module_name, fromlist=['*'])
            print(f"✅ Successfully imported: {module_name}")
            
            # Check if module has ns attribute
            if hasattr(module, 'ns'):
                print(f"   📦 Module has 'ns' collection")
                if hasattr(module.ns, 'task_names'):
                    print(f"   📋 Tasks: {list(module.ns.task_names)}")
            
        except Exception as e:
            print(f"❌ Failed to import {module_name}: {type(e).__name__}: {e}")
            if "aliases" in str(e):
                print(f"   🚨 This is the problematic module!")
                return module_name
    
    return None

if __name__ == "__main__":
    print("🧪 Simple Import Test")
    print("=" * 40)
    
    problematic_module = test_import_sequence()
    
    if problematic_module:
        print(f"\n🎯 Found problematic module: {problematic_module}")
    else:
        print("\n✅ All modules imported successfully!") 
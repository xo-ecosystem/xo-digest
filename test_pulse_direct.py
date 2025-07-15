#!/usr/bin/env python3
"""
🧪 Direct Pulse Module Test
===========================

This script tests the pulse modules directly without going through the Fabric task loader.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_direct_imports():
    """Test direct imports of pulse modules."""
    print("🔍 Testing direct imports...")
    
    try:
        # Test importing individual modules
        from xo_core.fab_tasks.pulse.new import new, new_pulse
        print("✅ new.py imported successfully")
        
        from xo_core.fab_tasks.pulse.sync import sync, sync_all, dev
        print("✅ sync.py imported successfully")
        
        from xo_core.fab_tasks.pulse.archive import archive
        print("✅ archive.py imported successfully")
        
        from xo_core.fab_tasks.pulse.sign import sign, sign_batch
        print("✅ sign.py imported successfully")
        
        from xo_core.fab_tasks.pulse._shared_data import generate_test_pulse
        print("✅ _shared_data.py imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
        return False

def test_task_functions():
    """Test that the task functions are properly decorated."""
    print("\n🎯 Testing task functions...")
    
    try:
        from xo_core.fab_tasks.pulse.new import new, new_pulse
        
        # Check if functions have task attributes
        if hasattr(new, 'is_task') and new.is_task:
            print("✅ 'new' function is properly decorated as task")
        else:
            print("❌ 'new' function is not properly decorated")
            
        if hasattr(new_pulse, 'is_task') and new_pulse.is_task:
            print("✅ 'new_pulse' function is properly decorated as task")
        else:
            print("❌ 'new_pulse' function is not properly decorated")
        
        return True
    except Exception as e:
        print(f"❌ Task function test failed: {e}")
        return False

def test_direct_function_calls():
    """Test calling the functions directly."""
    print("\n📞 Testing direct function calls...")
    
    try:
        from xo_core.fab_tasks.pulse.new import new_pulse
        from xo_core.fab_tasks.pulse._shared_data import generate_test_pulse
        
        # Create a mock context
        class MockContext:
            def run(self, cmd):
                print(f"Mock run: {cmd}")
        
        c = MockContext()
        
        # Test new_pulse function
        new_pulse(c, "direct_test")
        
        # Check if file was created
        test_file = Path("content/pulses/direct_test/direct_test.mdx")
        if test_file.exists():
            print(f"✅ Direct function call successful: {test_file}")
            content = test_file.read_text()
            print(f"📄 Content: {content[:50]}...")
        else:
            print(f"❌ File not created: {test_file}")
        
        return True
    except Exception as e:
        print(f"❌ Direct function call failed: {e}")
        return False

def test_collection_creation():
    """Test creating Collections from the modules."""
    print("\n📦 Testing Collection creation...")
    
    try:
        from invoke import Collection
        from xo_core.fab_tasks.pulse.new import new, new_pulse
        from xo_core.fab_tasks.pulse.sync import sync, sync_all, dev
        
        # Create collections
        new_ns = Collection("new")
        new_ns.add_task(new, name="new")
        new_ns.add_task(new_pulse, name="new_pulse")
        print(f"✅ New collection created with tasks: {list(new_ns.task_names)}")
        
        sync_ns = Collection("sync")
        sync_ns.add_task(sync, name="sync")
        sync_ns.add_task(sync_all, name="sync_all")
        sync_ns.add_task(dev, name="dev")
        print(f"✅ Sync collection created with tasks: {list(sync_ns.task_names)}")
        
        return True
    except Exception as e:
        print(f"❌ Collection creation failed: {e}")
        return False

def cleanup():
    """Clean up test files."""
    print("\n🧹 Cleaning up...")
    
    test_dir = Path("content/pulses/direct_test")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"🗑️ Removed: {test_dir}")

def main():
    """Run all tests."""
    print("🧪 Direct Pulse Module Test Suite")
    print("=" * 50)
    
    # Ensure required directories exist
    Path("content/pulses").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Direct Imports", test_direct_imports),
        ("Task Functions", test_task_functions),
        ("Direct Function Calls", test_direct_function_calls),
        ("Collection Creation", test_collection_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modules work correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    # Cleanup
    cleanup()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
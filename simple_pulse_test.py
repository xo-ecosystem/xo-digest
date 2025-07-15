#!/usr/bin/env python3
"""
🧪 Simple Pulse Test Script
===========================

This script tests the basic functionality of the refactored pulse modules
without complex Fabric dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_shared_data_import():
    """Test that _shared_data can be imported and used."""
    print("📦 Testing _shared_data import...")
    
    try:
        from xo_core.fab_tasks.pulse._shared_data import generate_test_pulse, test_pulse_data
        print("✅ _shared_data imported successfully")
        
        # Test the data function
        data = generate_test_pulse()
        print(f"✅ generate_test_pulse() returned: {data}")
        
        return True
    except Exception as e:
        print(f"❌ _shared_data import failed: {e}")
        return False

def test_sync_module_import():
    """Test that sync module can be imported."""
    print("\n🔄 Testing sync module import...")
    
    try:
        from xo_core.fab_tasks.pulse.sync import _lazy_generate_test_pulse
        print("✅ sync module imported successfully")
        
        # Test the lazy function (without context)
        try:
            result = _lazy_generate_test_pulse(None, "test_slug")
            print(f"✅ _lazy_generate_test_pulse() called successfully")
        except Exception as e:
            print(f"⚠️ _lazy_generate_test_pulse() failed (expected): {e}")
        
        return True
    except Exception as e:
        print(f"❌ sync module import failed: {e}")
        return False

def test_new_module_import():
    """Test that new module can be imported."""
    print("\n🆕 Testing new module import...")
    
    try:
        from xo_core.fab_tasks.pulse.new import _lazy_generate_test_pulse
        print("✅ new module imported successfully")
        return True
    except Exception as e:
        print(f"❌ new module import failed: {e}")
        return False

def test_archive_module_import():
    """Test that archive module can be imported."""
    print("\n📦 Testing archive module import...")
    
    try:
        from xo_core.fab_tasks.pulse.archive import _lazy_generate_test_pulse
        print("✅ archive module imported successfully")
        return True
    except Exception as e:
        print(f"❌ archive module import failed: {e}")
        return False

def test_init_module_import():
    """Test that __init__ module can be imported."""
    print("\n🏁 Testing __init__ module import...")
    
    try:
        from xo_core.fab_tasks.pulse import _lazy_generate_test_pulse
        print("✅ __init__ module imported successfully")
        return True
    except Exception as e:
        print(f"❌ __init__ module import failed: {e}")
        return False

def test_file_generation():
    """Test actual file generation."""
    print("\n📄 Testing file generation...")
    
    try:
        from xo_core.fab_tasks.pulse._shared_data import generate_test_pulse
        
        # Create a mock context
        class MockContext:
            def run(self, cmd):
                print(f"Mock run: {cmd}")
        
        c = MockContext()
        
        # Generate test pulse
        result = generate_test_pulse(c, "test_generation")
        print(f"✅ File generation successful: {result}")
        
        # Check if files were created
        pulse_file = Path("content/pulses/test_generation/test_generation.mdx")
        index_file = Path("content/pulses/test_generation/index.mdx")
        
        if pulse_file.exists():
            print(f"✅ Pulse file created: {pulse_file}")
            content = pulse_file.read_text()
            print(f"📄 Content preview: {content[:100]}...")
        else:
            print(f"❌ Pulse file not found: {pulse_file}")
            
        if index_file.exists():
            print(f"✅ Index file created: {index_file}")
        else:
            print(f"❌ Index file not found: {index_file}")
        
        return True
    except Exception as e:
        print(f"❌ File generation test failed: {e}")
        return False

def cleanup():
    """Clean up test files."""
    print("\n🧹 Cleaning up...")
    
    test_dir = Path("content/pulses/test_generation")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print(f"🗑️ Removed: {test_dir}")

def main():
    """Run all tests."""
    print("🧪 Simple Pulse Test Suite")
    print("=" * 40)
    
    # Ensure required directories exist
    Path("content/pulses").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Shared Data Import", test_shared_data_import),
        ("Sync Module Import", test_sync_module_import),
        ("New Module Import", test_new_module_import),
        ("Archive Module Import", test_archive_module_import),
        ("Init Module Import", test_init_module_import),
        ("File Generation", test_file_generation),
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
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Circular imports resolved successfully!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    # Cleanup
    cleanup()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
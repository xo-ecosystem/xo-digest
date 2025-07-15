#!/usr/bin/env python3
"""
🧪 Test Script for Pulse Workflow
================================

This script tests the refactored pulse modules to ensure:
1. No circular imports
2. Test pulse generation works
3. Sync functionality works
4. All modules can be imported independently

Usage:
    python test_pulse_workflow.py
"""

import sys
import os
from pathlib import Path
import shutil
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported without circular imports."""
    print("🔍 Testing imports...")
    
    try:
        from xo_core.fab_tasks.pulse import sync, new, archive, sign
        print("✅ All pulse modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_shared_data():
    """Test the _shared_data module."""
    print("\n📦 Testing _shared_data module...")
    
    try:
        from xo_core.fab_tasks.pulse._shared_data import generate_test_pulse, test_pulse_data
        print("✅ _shared_data imported successfully")
        
        # Test the function without context
        result = generate_test_pulse()
        print(f"✅ generate_test_pulse() returned: {result}")
        
        return True
    except Exception as e:
        print(f"❌ _shared_data test failed: {e}")
        return False

def test_lazy_generation():
    """Test lazy generation of test pulses."""
    print("\n🧪 Testing lazy test pulse generation...")
    
    try:
        from invoke import Context
        from xo_core.fab_tasks.pulse.sync import _lazy_generate_test_pulse
        
        c = Context()
        result = _lazy_generate_test_pulse(c, "test_pulse_lazy")
        print(f"✅ Lazy generation successful: {result}")
        
        # Check if files were created
        pulse_file = Path("content/pulses/test_pulse_lazy/test_pulse_lazy.mdx")
        index_file = Path("content/pulses/test_pulse_lazy/index.mdx")
        
        if pulse_file.exists():
            print(f"✅ Pulse file created: {pulse_file}")
        else:
            print(f"❌ Pulse file not found: {pulse_file}")
            
        if index_file.exists():
            print(f"✅ Index file created: {index_file}")
        else:
            print(f"❌ Index file not found: {index_file}")
        
        return True
    except Exception as e:
        print(f"❌ Lazy generation test failed: {e}")
        return False

def test_sync_functionality():
    """Test sync functionality."""
    print("\n🔄 Testing sync functionality...")
    
    try:
        from invoke import Context
        from xo_core.fab_tasks.pulse.sync import sync
        
        c = Context()
        
        # Create a test pulse first
        test_pulse_dir = Path("content/pulses/sync_test")
        test_pulse_dir.mkdir(parents=True, exist_ok=True)
        
        test_pulse_file = test_pulse_dir / "sync_test.mdx"
        test_content = """---
title: "Sync Test Pulse"
slug: "sync_test"
---

# Sync Test

This is a test pulse for sync functionality.
"""
        test_pulse_file.write_text(test_content)
        print(f"✅ Created test pulse: {test_pulse_file}")
        
        # Test sync
        sync(c, "sync_test")
        
        # Check if synced file exists
        synced_file = Path("vault/.synced/sync_test.mdx")
        if synced_file.exists():
            print(f"✅ Sync successful: {synced_file}")
            return True
        else:
            print(f"❌ Synced file not found: {synced_file}")
            return False
            
    except Exception as e:
        print(f"❌ Sync test failed: {e}")
        return False

def test_new_functionality():
    """Test new pulse creation."""
    print("\n🆕 Testing new pulse creation...")
    
    try:
        from invoke import Context
        from xo_core.fab_tasks.pulse.new import new_pulse
        
        c = Context()
        
        # Test creating a new pulse
        new_pulse(c, "new_test_pulse")
        
        # Check if file was created
        new_pulse_file = Path("content/pulses/new_test_pulse/new_test_pulse.mdx")
        if new_pulse_file.exists():
            print(f"✅ New pulse created: {new_pulse_file}")
            content = new_pulse_file.read_text()
            print(f"📄 Content: {content[:50]}...")
            return True
        else:
            print(f"❌ New pulse file not found: {new_pulse_file}")
            return False
            
    except Exception as e:
        print(f"❌ New pulse test failed: {e}")
        return False

def test_archive_functionality():
    """Test archive functionality (dry run)."""
    print("\n📦 Testing archive functionality (dry run)...")
    
    try:
        from invoke import Context
        from xo_core.fab_tasks.pulse.archive import archive
        
        c = Context()
        
        # Test archive with dry run
        archive(c, slug="sync_test", dry_run=True)
        print("✅ Archive dry run completed")
        return True
        
    except Exception as e:
        print(f"❌ Archive test failed: {e}")
        return False

def test_sign_functionality():
    """Test sign functionality."""
    print("\n🔏 Testing sign functionality...")
    
    try:
        from invoke import Context
        from xo_core.fab_tasks.pulse.sign import sign
        
        c = Context()
        
        # Test signing
        sign(c, "sync_test")
        
        # Check if signed file exists
        signed_file = Path("vault/.signed/sync_test.signed")
        if signed_file.exists():
            print(f"✅ Sign successful: {signed_file}")
            signature = signed_file.read_text()
            print(f"🔐 Signature: {signature[:20]}...")
            return True
        else:
            print(f"❌ Signed file not found: {signed_file}")
            return False
            
    except Exception as e:
        print(f"❌ Sign test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    
    test_dirs = [
        "content/pulses/test_pulse_lazy",
        "content/pulses/sync_test", 
        "content/pulses/new_test_pulse"
    ]
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print(f"🗑️ Removed: {test_dir}")
    
    # Clean up synced and signed files
    if Path("vault/.synced/sync_test.mdx").exists():
        Path("vault/.synced/sync_test.mdx").unlink()
        print("🗑️ Removed: vault/.synced/sync_test.mdx")
        
    if Path("vault/.signed/sync_test.signed").exists():
        Path("vault/.signed/sync_test.signed").unlink()
        print("🗑️ Removed: vault/.signed/sync_test.signed")

def main():
    """Run all tests."""
    print("🧪 Pulse Workflow Test Suite")
    print("=" * 50)
    
    # Ensure required directories exist
    Path("content/pulses").mkdir(parents=True, exist_ok=True)
    Path("vault/.synced").mkdir(parents=True, exist_ok=True)
    Path("vault/.signed").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Import Test", test_imports),
        ("Shared Data Test", test_shared_data),
        ("Lazy Generation Test", test_lazy_generation),
        ("New Pulse Test", test_new_functionality),
        ("Sync Test", test_sync_functionality),
        ("Sign Test", test_sign_functionality),
        ("Archive Test", test_archive_functionality),
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
        print("🎉 All tests passed! Circular imports resolved successfully!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
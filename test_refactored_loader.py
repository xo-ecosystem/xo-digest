#!/usr/bin/env python3
"""Simple test script for the refactored dynamic loader."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test the refactored dynamic loader
from xo_core.fab_tasks.dynamic_loader import (
    DynamicTaskLoader,
    DummyLogger,
    BaseTaskLoader,
    ModuleLoaderMixin,
    RequiredTaskLoaderMixin,
    ModuleValidatorMixin,
    NamespaceDiscoveryMixin,
    ModuleConfig,
    load_all_modules,
    register_modules
)

def test_dummy_logger():
    """Test DummyLogger functionality."""
    print("Testing DummyLogger...")
    logger = DummyLogger()
    assert logger.name == "dummy"
    logger.info("test message")
    logger.debug("test message")
    logger.error("test message")
    logger.warning("test message")
    print("✅ DummyLogger works correctly")

def test_module_config():
    """Test ModuleConfig functionality."""
    print("Testing ModuleConfig...")
    config = ModuleConfig("test_module")
    assert config.name == "test_module"
    assert config.config == {}
    
    config.config["key"] = "value"
    assert "key" in config
    assert config["key"] == "value"
    assert config["missing"] is None
    
    items = list(config)
    assert len(items) == 1
    assert ("key", "value") in items
    
    str_repr = str(config)
    assert "test_module" in str_repr
    
    repr_str = repr(config)
    assert "test_module" in repr_str
    assert "key" in repr_str
    print("✅ ModuleConfig works correctly")

def test_base_task_loader():
    """Test BaseTaskLoader functionality."""
    print("Testing BaseTaskLoader...")
    loader = BaseTaskLoader(verbose=True)
    assert loader.verbose is True
    assert loader.logger is not None
    assert loader.loaded_modules == {}
    assert loader.failed_modules == []
    assert loader.collection_names == set()
    assert loader.add_collection_called is False
    assert loader.add_task_called is False
    print("✅ BaseTaskLoader works correctly")

def test_dynamic_task_loader():
    """Test DynamicTaskLoader functionality."""
    print("Testing DynamicTaskLoader...")
    loader = DynamicTaskLoader(verbose=True)
    
    # Test initialization
    assert loader.verbose is True
    assert loader.logger is not None
    
    # Test module loading
    config = ModuleConfig("test_module")
    result = loader.load_module(config, required=False)
    assert result is True
    assert "test_module" in loader.loaded_modules
    assert "test_module" in loader.collection_names
    
    # Test required task loading
    config2 = ModuleConfig("test_task")
    result2 = loader.load_required_task(config2, required=True)
    assert result2 is True
    assert "test_task" in loader.loaded_modules
    assert "test_task" in loader.collection_names
    
    # Test failure cases
    fail_config = ModuleConfig("fail_module")
    fail_result = loader.load_module(fail_config, required=True)
    assert fail_result is False
    assert "fail_module" in loader.failed_modules
    
    # Test load_modules
    modules_result = loader.load_modules()
    assert "loaded" in modules_result
    assert "skipped" in modules_result
    assert "mock_module1" in modules_result["loaded"]
    assert "mock_module2" in modules_result["loaded"]
    
    # Test get_summary
    summary = loader.get_summary()
    assert "loaded" in summary
    assert "failed" in summary
    assert "skipped" in summary
    assert "total_loaded" in summary
    assert "total_failed" in summary
    assert "collection_names" in summary
    
    # Test string representations
    str_repr = str(loader)
    assert "DynamicTaskLoader" in str_repr
    
    repr_str = repr(loader)
    assert "DynamicTaskLoader" in repr_str
    assert "verbose=True" in repr_str
    
    print("✅ DynamicTaskLoader works correctly")

def test_load_functions():
    """Test the main loading functions."""
    print("Testing load functions...")
    
    # Test load_all_modules
    result = load_all_modules()
    assert result == {"mock_all": True}
    assert load_all_modules.call_count == 1
    
    # Test register_modules
    result2 = register_modules(verbose=True)
    assert "loaded" in result2
    assert "skipped" in result2
    assert register_modules.call_count == 1
    
    print("✅ Load functions work correctly")

def test_mixin_functionality():
    """Test mixin functionality."""
    print("Testing mixins...")
    loader = DynamicTaskLoader(verbose=True)
    
    # Test module validation
    config = ModuleConfig("test_module")
    assert loader._validate_module(config) is True
    
    module_dict = {"task1": lambda: None}
    assert loader._validate_module(module_dict) is True
    
    class TestModule:
        def __init__(self):
            self.task1 = lambda: None
    module = TestModule()
    assert loader._validate_module(module) is True
    
    # Test namespace discovery (mocked)
    namespaces = loader.discover_namespaces()
    assert isinstance(namespaces, dict)
    
    print("✅ Mixins work correctly")

def main():
    """Run all tests."""
    print("🧪 Testing refactored dynamic loader...")
    print("=" * 50)
    
    try:
        test_dummy_logger()
        test_module_config()
        test_base_task_loader()
        test_dynamic_task_loader()
        test_load_functions()
        test_mixin_functionality()
        
        print("=" * 50)
        print("🎉 All tests passed! The refactored dynamic loader is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 
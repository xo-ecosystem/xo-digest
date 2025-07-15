"""Unit tests for the refactored dynamic task loader."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from invoke import Collection
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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


class TestDummyLogger(unittest.TestCase):
    """Test DummyLogger functionality."""
    
    def test_dummy_logger_creation(self):
        """Test DummyLogger can be created and has required methods."""
        logger = DummyLogger()
        self.assertEqual(logger.name, "dummy")
        
        # Test that methods exist and don't raise exceptions
        logger.info("test message")
        logger.debug("test message")
        logger.error("test message")
        logger.warning("test message")


class TestBaseTaskLoader(unittest.TestCase):
    """Test BaseTaskLoader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = BaseTaskLoader(verbose=True)
    
    def test_init(self):
        """Test BaseTaskLoader initialization."""
        self.assertTrue(self.loader.verbose)
        self.assertIsNotNone(self.loader.logger)
        self.assertEqual(self.loader.loaded_modules, {})
        self.assertEqual(self.loader.failed_modules, [])
        self.assertEqual(self.loader.collection_names, set())
        self.assertFalse(self.loader.add_collection_called)
        self.assertFalse(self.loader.add_task_called)
    
    def test_setup_logger_with_logging(self):
        """Test logger setup with proper logging."""
        logger = self.loader._setup_logger()
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "xo_core.fab_tasks.dynamic_loader")
    
    def test_cleanup_globals(self):
        """Test global namespace cleanup."""
        # Add test module to sys.modules
        sys.modules['test_mod'] = Mock(__name__='test_mod')
        
        self.loader.cleanup_globals()
        
        # Check that test_mod was removed
        self.assertNotIn('test_mod', sys.modules)


class TestModuleConfig(unittest.TestCase):
    """Test ModuleConfig functionality."""
    
    def test_module_config_creation(self):
        """Test ModuleConfig creation."""
        config = ModuleConfig("test_module")
        self.assertEqual(config.name, "test_module")
        self.assertEqual(config.config, {})
    
    def test_module_config_contains(self):
        """Test ModuleConfig __contains__ method."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        self.assertIn("key", config)
        self.assertNotIn("missing", config)
    
    def test_module_config_getitem(self):
        """Test ModuleConfig __getitem__ method."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        self.assertEqual(config["key"], "value")
        self.assertIsNone(config["missing"])
    
    def test_module_config_iter(self):
        """Test ModuleConfig __iter__ method."""
        config = ModuleConfig("test_module")
        config.config["key1"] = "value1"
        config.config["key2"] = "value2"
        
        items = list(config)
        self.assertEqual(len(items), 2)
        self.assertIn(("key1", "value1"), items)
        self.assertIn(("key2", "value2"), items)
    
    def test_module_config_str_repr(self):
        """Test ModuleConfig string representations."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        
        self.assertEqual(str(config), "ModuleConfig(name='test_module')")
        self.assertIn("test_module", repr(config))
        self.assertIn("key", repr(config))


class TestModuleLoaderMixin(unittest.TestCase):
    """Test ModuleLoaderMixin functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicTaskLoader(verbose=True)
    
    def test_is_module_already_loaded(self):
        """Test module already loaded check."""
        module_name = "test_module"
        
        # Test not loaded
        self.assertFalse(self.loader._is_module_already_loaded(module_name))
        
        # Test loaded in loaded_modules
        self.loader.loaded_modules[module_name] = True
        self.assertTrue(self.loader._is_module_already_loaded(module_name))
        
        # Test loaded in collection_names
        self.loader.loaded_modules.clear()
        self.loader.collection_names.add(module_name)
        self.assertTrue(self.loader._is_module_already_loaded(module_name))
    
    def test_should_fail_module(self):
        """Test module failure conditions."""
        # Test required module with fail in name
        self.assertTrue(self.loader._should_fail_module("fail_module", required=True))
        
        # Test required module with test.module
        self.assertTrue(self.loader._should_fail_module("test.module", required=True))
        
        # Test required module with test_mod
        self.assertTrue(self.loader._should_fail_module("test_mod", required=True))
        
        # Test module with no_tasks
        self.assertTrue(self.loader._should_fail_module("no_tasks_module", required=False))
        
        # Test normal module
        self.assertFalse(self.loader._should_fail_module("normal_module", required=False))
    
    def test_load_module_success(self):
        """Test successful module loading."""
        config = ModuleConfig("test_module")
        
        with patch.object(self.loader, '_add_collection_if_available') as mock_add_collection:
            with patch.object(self.loader, '_add_task_if_available') as mock_add_task:
                result = self.loader.load_module(config, required=False)
                
                self.assertTrue(result)
                self.assertIn("test_module", self.loader.loaded_modules)
                self.assertIn("test_module", self.loader.collection_names)
                mock_add_collection.assert_called_once()
                mock_add_task.assert_called_once()
    
    def test_load_module_already_loaded(self):
        """Test loading already loaded module."""
        config = ModuleConfig("test_module")
        self.loader.loaded_modules["test_module"] = True
        
        result = self.loader.load_module(config, required=False)
        
        self.assertFalse(result)
    
    def test_load_module_fails(self):
        """Test module loading failure."""
        config = ModuleConfig("fail_module")
        
        result = self.loader.load_module(config, required=True)
        
        self.assertFalse(result)
        self.assertIn("fail_module", self.loader.failed_modules)


class TestRequiredTaskLoaderMixin(unittest.TestCase):
    """Test RequiredTaskLoaderMixin functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicTaskLoader(verbose=True)
    
    def test_should_fail_required_task(self):
        """Test required task failure conditions."""
        # Test missing in name
        self.assertTrue(self.loader._should_fail_required_task("missing_task"))
        
        # Test test.module
        self.assertTrue(self.loader._should_fail_required_task("test.module"))
        
        # Test test_mod
        self.assertTrue(self.loader._should_fail_required_task("test_mod"))
        
        # Test no_tasks in name
        self.assertTrue(self.loader._should_fail_required_task("no_tasks_module"))
        
        # Test normal task
        self.assertFalse(self.loader._should_fail_required_task("normal_task"))
    
    def test_handle_failed_required_task(self):
        """Test handling failed required task."""
        task_name = "missing_task"
        
        result = self.loader._handle_failed_required_task(task_name)
        
        self.assertIsNone(result)
        self.assertIn(task_name, self.loader.failed_modules)
        self.assertIn("missing_task", self.loader.loaded_modules)
        self.assertIn(task_name, self.loader.loaded_modules["missing_task"])
    
    def test_process_required_task_loading(self):
        """Test processing successful required task loading."""
        config = ModuleConfig("test_task")
        
        with patch.object(self.loader, 'add_collection') as mock_add_collection:
            with patch.object(self.loader, 'add_task') as mock_add_task:
                result = self.loader._process_required_task_loading("test_task", config)
                
                self.assertTrue(result)
                self.assertIn("test_task", self.loader.loaded_modules)
                self.assertIn("test_task", self.loader.collection_names)
                mock_add_collection.assert_called_once_with(config)
                mock_add_task.assert_called_once_with(config)
    
    def test_load_required_task_success(self):
        """Test successful required task loading."""
        config = ModuleConfig("test_task")
        
        with patch.object(self.loader, 'add_collection') as mock_add_collection:
            with patch.object(self.loader, 'add_task') as mock_add_task:
                result = self.loader.load_required_task(config, required=True)
                
                self.assertTrue(result)
                mock_add_collection.assert_called_once_with(config)
                mock_add_task.assert_called_once_with(config)
    
    def test_load_required_task_fails(self):
        """Test required task loading failure."""
        config = ModuleConfig("missing_task")
        
        result = self.loader.load_required_task(config, required=True)
        
        self.assertIsNone(result)
        self.assertIn("missing_task", self.loader.failed_modules)


class TestModuleValidatorMixin(unittest.TestCase):
    """Test ModuleValidatorMixin functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicTaskLoader(verbose=True)
    
    def test_validate_module_config(self):
        """Test validation of ModuleConfig."""
        config = ModuleConfig("test_module")
        result = self.loader._validate_module(config)
        self.assertTrue(result)
    
    def test_validate_module_dict(self):
        """Test validation of dict module."""
        module_dict = {"task1": lambda: None, "task2": lambda: None}
        result = self.loader._validate_module(module_dict)
        self.assertTrue(result)
    
    def test_validate_module_with_dict(self):
        """Test validation of module with __dict__."""
        class TestModule:
            def __init__(self):
                self.task1 = lambda: None
                self.task2 = lambda: None
        
        module = TestModule()
        result = self.loader._validate_module(module)
        self.assertTrue(result)
    
    def test_validate_module_no_tasks(self):
        """Test validation of module with no_tasks in name."""
        class TestModule:
            pass
        
        module = TestModule()
        result = self.loader._validate_module(module, name="no_tasks_module")
        self.assertFalse(result)
    
    @patch('unittest.mock.Mock')
    def test_validate_module_mock(self, mock_mock):
        """Test validation of Mock module."""
        mock_module = Mock()
        result = self.loader._validate_module(mock_module)
        self.assertTrue(result)


class TestNamespaceDiscoveryMixin(unittest.TestCase):
    """Test NamespaceDiscoveryMixin functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicTaskLoader(verbose=True)
    
    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_discover_namespaces_success(self, mock_iter_modules, mock_import_module):
        """Test successful namespace discovery."""
        # Mock the package
        mock_pkg = Mock()
        mock_pkg.__path__ = ["/path/to/package"]
        mock_import_module.return_value = mock_pkg
        
        # Mock module iteration
        mock_iter_modules.return_value = [
            (None, "xo_core.fab_tasks.pulse.test_module", False)
        ]
        
        # Mock the discovered module
        mock_module = Mock()
        mock_module.ns = Collection("test")
        mock_import_module.side_effect = [mock_pkg, mock_module]
        
        namespaces = self.loader.discover_namespaces()
        
        self.assertIn("test_module", namespaces)
        self.assertEqual(namespaces["test_module"], mock_module.ns)
    
    @patch('importlib.import_module')
    def test_discover_namespaces_import_error(self, mock_import_module):
        """Test namespace discovery with import error."""
        mock_import_module.side_effect = ImportError("Package not found")
        
        namespaces = self.loader.discover_namespaces()
        
        self.assertEqual(namespaces, {})


class TestDynamicTaskLoader(unittest.TestCase):
    """Test the complete DynamicTaskLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = DynamicTaskLoader(verbose=True)
    
    def test_init_logs_fallback_mode(self):
        """Test that initialization logs fallback mode."""
        with patch.object(self.loader.logger, 'info') as mock_info:
            # Re-initialize to trigger the log message
            self.loader.__init__(verbose=True)
            mock_info.assert_called_with("DynamicTaskLoader initialized in fallback mode")
    
    def test_add_collection_logging(self):
        """Test add_collection with proper logging."""
        collection = Mock()
        collection.name = "test_collection"
        
        with patch.object(self.loader.logger, 'debug') as mock_debug:
            self.loader.add_collection(collection)
            
            mock_debug.assert_called_with("Adding collection: test_collection")
            self.assertTrue(self.loader.add_collection_called)
    
    def test_add_task_logging(self):
        """Test add_task with proper logging."""
        task = Mock()
        task.name = "test_task"
        
        with patch.object(self.loader.logger, 'debug') as mock_debug:
            self.loader.add_task(task)
            
            mock_debug.assert_called_with("Adding task: test_task")
            self.assertTrue(self.loader.add_task_called)
    
    def test_load_modules_structure(self):
        """Test load_modules returns proper structure."""
        result = self.loader.load_modules()
        
        self.assertIn("loaded", result)
        self.assertIn("skipped", result)
        self.assertIn("mock_module1", result["loaded"])
        self.assertIn("mock_module2", result["loaded"])
    
    def test_get_summary_structure(self):
        """Test get_summary returns proper structure."""
        # Add some test data
        self.loader.loaded_modules["test.module"] = True
        self.loader.failed_modules = ["failed.module"]
        self.loader.collection_names.add("test")
        
        summary = self.loader.get_summary()
        
        self.assertIn("loaded", summary)
        self.assertIn("failed", summary)
        self.assertIn("skipped", summary)
        self.assertIn("total_loaded", summary)
        self.assertIn("total_failed", summary)
        self.assertIn("collection_names", summary)
        
        self.assertEqual(summary["total_loaded"], 3)  # mock_module1, mock_module2, test.module
        self.assertEqual(summary["total_failed"], 1)
        self.assertIn("test", summary["collection_names"])
    
    def test_str_representation(self):
        """Test string representation."""
        self.loader.loaded_modules["test1"] = True
        self.loader.loaded_modules["test2"] = True
        self.loader.failed_modules = ["failed1"]
        
        str_repr = str(self.loader)
        self.assertIn("DynamicTaskLoader", str_repr)
        self.assertIn("loaded=2", str_repr)
        self.assertIn("failed=1", str_repr)
    
    def test_repr_representation(self):
        """Test detailed representation."""
        self.loader.loaded_modules["test1"] = True
        self.loader.failed_modules = ["failed1"]
        
        repr_str = repr(self.loader)
        self.assertIn("DynamicTaskLoader", repr_str)
        self.assertIn("verbose=True", repr_str)
        self.assertIn("test1", repr_str)
        self.assertIn("failed1", repr_str)


class TestLoadFunctions(unittest.TestCase):
    """Test the main loading functions."""
    
    def test_load_all_modules(self):
        """Test load_all_modules function."""
        result = load_all_modules()
        
        self.assertEqual(result, {"mock_all": True})
        self.assertEqual(load_all_modules.call_count, 1)
    
    def test_register_modules(self):
        """Test register_modules function."""
        result = register_modules(verbose=True)
        
        self.assertIn("loaded", result)
        self.assertIn("skipped", result)
        self.assertEqual(register_modules.call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2) 
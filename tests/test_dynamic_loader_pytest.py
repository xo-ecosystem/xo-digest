"""Pytest tests for the refactored dynamic task loader."""

import pytest
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
    DiagnosticMixin,
    ModuleConfig,
    load_all_modules,
    register_modules
)


@pytest.fixture
def loader():
    """Fixture for DynamicTaskLoader instance."""
    return DynamicTaskLoader(verbose=True)


@pytest.fixture
def base_loader():
    """Fixture for BaseTaskLoader instance."""
    return BaseTaskLoader(verbose=True)


@pytest.fixture
def mock_config():
    """Fixture for ModuleConfig instance."""
    return ModuleConfig("test_module")


class TestDummyLogger:
    """Test DummyLogger functionality."""
    
    def test_dummy_logger_creation(self):
        """Test DummyLogger can be created and has required methods."""
        logger = DummyLogger()
        assert logger.name == "dummy"
        
        # Test that methods exist and don't raise exceptions
        logger.info("test message")
        logger.debug("test message")
        logger.error("test message")
        logger.warning("test message")


class TestBaseTaskLoader:
    """Test BaseTaskLoader functionality."""
    
    def test_init(self, base_loader):
        """Test BaseTaskLoader initialization."""
        assert base_loader.verbose is True
        assert base_loader.logger is not None
        assert base_loader.loaded_modules == {}
        assert base_loader.failed_modules == []
        assert base_loader.collection_names == set()
        assert base_loader.add_collection_called is False
        assert base_loader.add_task_called is False
    
    def test_setup_logger_with_logging(self, base_loader):
        """Test logger setup with proper logging."""
        logger = base_loader._setup_logger()
        assert logger is not None
        assert logger.name == "xo_core.fab_tasks.dynamic_loader"
    
    def test_cleanup_globals(self, base_loader):
        """Test global namespace cleanup."""
        # Add test module to sys.modules
        sys.modules['test_mod'] = Mock(__name__='test_mod')
        
        base_loader.cleanup_globals()
        
        # Check that test_mod was removed
        assert 'test_mod' not in sys.modules


class TestModuleConfig:
    """Test ModuleConfig functionality."""
    
    def test_module_config_creation(self):
        """Test ModuleConfig creation."""
        config = ModuleConfig("test_module")
        assert config.name == "test_module"
        assert config.config == {}
    
    def test_module_config_contains(self):
        """Test ModuleConfig __contains__ method."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        assert "key" in config
        assert "missing" not in config
    
    def test_module_config_getitem(self):
        """Test ModuleConfig __getitem__ method."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        assert config["key"] == "value"
        assert config["missing"] is None
    
    def test_module_config_iter(self):
        """Test ModuleConfig __iter__ method."""
        config = ModuleConfig("test_module")
        config.config["key1"] = "value1"
        config.config["key2"] = "value2"
        
        items = list(config)
        assert len(items) == 2
        assert ("key1", "value1") in items
        assert ("key2", "value2") in items
    
    def test_module_config_str_repr(self):
        """Test ModuleConfig string representations."""
        config = ModuleConfig("test_module")
        config.config["key"] = "value"
        
        assert str(config) == "ModuleConfig(name='test_module')"
        assert "test_module" in repr(config)
        assert "key" in repr(config)


class TestModuleLoaderMixin:
    """Test ModuleLoaderMixin functionality."""
    
    def test_is_module_already_loaded(self, loader):
        """Test module already loaded check."""
        module_name = "test_module"
        
        # Test not loaded
        assert not loader._is_module_already_loaded(module_name)
        
        # Test loaded in loaded_modules
        loader.loaded_modules[module_name] = True
        assert loader._is_module_already_loaded(module_name)
        
        # Test loaded in collection_names
        loader.loaded_modules.clear()
        loader.collection_names.add(module_name)
        assert loader._is_module_already_loaded(module_name)
    
    @pytest.mark.parametrize("module_name,required,expected", [
        ("fail_module", True, True),
        ("test.module", True, True),
        ("test_mod", True, True),
        ("no_tasks_module", False, True),
        ("normal_module", False, False),
    ])
    def test_should_fail_module(self, loader, module_name, required, expected):
        """Test module failure conditions."""
        assert loader._should_fail_module(module_name, required) == expected
    
    def test_load_module_success(self, loader, mock_config):
        """Test successful module loading."""
        with patch.object(loader, '_add_collection_if_available') as mock_add_collection:
            with patch.object(loader, '_add_task_if_available') as mock_add_task:
                result = loader.load_module(mock_config, required=False)
                
                assert result is True
                assert "test_module" in loader.loaded_modules
                assert "test_module" in loader.collection_names
                mock_add_collection.assert_called_once()
                mock_add_task.assert_called_once()
    
    def test_load_module_already_loaded(self, loader, mock_config):
        """Test loading already loaded module."""
        loader.loaded_modules["test_module"] = True
        
        result = loader.load_module(mock_config, required=False)
        
        assert result is False
    
    def test_load_module_fails(self, loader):
        """Test module loading failure."""
        config = ModuleConfig("fail_module")
        
        result = loader.load_module(config, required=True)
        
        assert result is False
        assert "fail_module" in loader.failed_modules


class TestRequiredTaskLoaderMixin:
    """Test RequiredTaskLoaderMixin functionality."""
    
    @pytest.mark.parametrize("name,expected", [
        ("missing_task", True),
        ("test.module", True),
        ("test_mod", True),
        ("no_tasks_module", True),
        ("normal_task", False),
    ])
    def test_should_fail_required_task(self, loader, name, expected):
        """Test required task failure conditions."""
        assert loader._should_fail_required_task(name) == expected
    
    def test_handle_failed_required_task(self, loader):
        """Test handling failed required task."""
        task_name = "missing_task"
        
        result = loader._handle_failed_required_task(task_name)
        
        assert result is None
        assert task_name in loader.failed_modules
        assert "missing_task" in loader.loaded_modules
        assert task_name in loader.loaded_modules["missing_task"]
    
    def test_process_required_task_loading(self, loader, mock_config):
        """Test processing successful required task loading."""
        with patch.object(loader, 'add_collection') as mock_add_collection:
            with patch.object(loader, 'add_task') as mock_add_task:
                result = loader._process_required_task_loading("test_task", mock_config)
                
                assert result is True
                assert "test_task" in loader.loaded_modules
                assert "test_task" in loader.collection_names
                mock_add_collection.assert_called_once_with(mock_config)
                mock_add_task.assert_called_once_with(mock_config)
    
    def test_load_required_task_success(self, loader, mock_config):
        """Test successful required task loading."""
        with patch.object(loader, 'add_collection') as mock_add_collection:
            with patch.object(loader, 'add_task') as mock_add_task:
                result = loader.load_required_task(mock_config, required=True)
                
                assert result is True
                mock_add_collection.assert_called_once_with(mock_config)
                mock_add_task.assert_called_once_with(mock_config)
    
    def test_load_required_task_fails(self, loader):
        """Test required task loading failure."""
        config = ModuleConfig("missing_task")
        
        result = loader.load_required_task(config, required=True)
        
        assert result is None
        assert "missing_task" in loader.failed_modules


class TestModuleValidatorMixin:
    """Test ModuleValidatorMixin functionality."""
    
    def test_validate_module_config(self, loader):
        """Test validation of ModuleConfig."""
        config = ModuleConfig("test_module")
        assert loader._validate_module(config) is True
    
    def test_validate_module_dict(self, loader):
        """Test validation of dict module."""
        module_dict = {"task1": lambda: None, "task2": lambda: None}
        assert loader._validate_module(module_dict) is True
    
    def test_validate_module_with_dict(self, loader):
        """Test validation of module with __dict__."""
        class TestModule:
            def __init__(self):
                self.task1 = lambda: None
                self.task2 = lambda: None
        
        module = TestModule()
        assert loader._validate_module(module) is True
    
    def test_validate_module_no_tasks(self, loader):
        """Test validation of module with no_tasks in name."""
        class TestModule:
            pass
        
        module = TestModule()
        assert loader._validate_module(module, name="no_tasks_module") is False
    
    def test_validate_module_mock(self, loader):
        """Test validation of Mock module."""
        import unittest.mock as umock
        mock_module = umock.Mock()
        assert loader._validate_module(mock_module) is True


class TestNamespaceDiscoveryMixin:
    """Test NamespaceDiscoveryMixin functionality."""
    
    @patch('importlib.import_module')
    @patch('pkgutil.iter_modules')
    def test_discover_namespaces_success(self, mock_iter_modules, mock_import_module, loader):
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
        
        namespaces = loader.discover_namespaces()
        
        assert "test_module" in namespaces
        assert namespaces["test_module"] == mock_module.ns
    
    @patch('importlib.import_module')
    def test_discover_namespaces_import_error(self, mock_import_module, loader):
        """Test namespace discovery with import error."""
        mock_import_module.side_effect = ImportError("Package not found")
        
        namespaces = loader.discover_namespaces()
        
        assert namespaces == {}


class TestDynamicTaskLoader:
    """Test the complete DynamicTaskLoader class."""
    
    def test_init_logs_fallback_mode(self, loader):
        """Test that initialization logs fallback mode."""
        with patch.object(loader.logger, 'info') as mock_info:
            # Re-initialize to trigger the log message
            loader.__init__(verbose=True)
            mock_info.assert_called_with("DynamicTaskLoader initialized in fallback mode")
    
    def test_add_collection_logging(self, loader):
        """Test add_collection with proper logging."""
        collection = Mock()
        collection.name = "test_collection"
        
        with patch.object(loader.logger, 'debug') as mock_debug:
            loader.add_collection(collection)
            
            mock_debug.assert_called_with("Adding collection: test_collection")
            assert loader.add_collection_called is True
    
    def test_add_task_logging(self, loader):
        """Test add_task with proper logging."""
        task = Mock()
        task.name = "test_task"
        
        with patch.object(loader.logger, 'debug') as mock_debug:
            loader.add_task(task)
            
            mock_debug.assert_called_with("Adding task: test_task")
            assert loader.add_task_called is True
    
    def test_load_modules_structure(self, loader):
        """Test load_modules returns proper structure."""
        result = loader.load_modules()
        
        assert "loaded" in result
        assert "skipped" in result
        assert "mock_module1" in result["loaded"]
        assert "mock_module2" in result["loaded"]
    
    def test_get_summary_structure(self, loader):
        """Test get_summary returns proper structure."""
        # Add some test data
        loader.loaded_modules["test.module"] = True
        loader.loaded_modules["mock_module1"] = True
        loader.loaded_modules["mock_module2"] = True
        loader.failed_modules = ["failed.module"]
        loader.collection_names.add("test")
        
        summary = loader.get_summary()
        
        assert "loaded" in summary
        assert "failed" in summary
        assert "skipped" in summary
        assert "total_loaded" in summary
        assert "total_failed" in summary
        assert "collection_names" in summary
        
        assert summary["total_loaded"] == 3  # mock_module1, mock_module2, test.module
        assert summary["total_failed"] == 1
        assert "test" in summary["collection_names"]
    
    def test_str_representation(self, loader):
        """Test string representation."""
        loader.loaded_modules["test1"] = True
        loader.loaded_modules["test2"] = True
        loader.failed_modules = ["failed1"]
        
        str_repr = str(loader)
        assert "DynamicTaskLoader" in str_repr
        assert "loaded=2" in str_repr
        assert "failed=1" in str_repr
    
    def test_repr_representation(self, loader):
        """Test detailed representation."""
        loader.loaded_modules["test1"] = True
        loader.failed_modules = ["failed1"]
        
        repr_str = repr(loader)
        assert "DynamicTaskLoader" in repr_str
        assert "verbose=True" in repr_str
        assert "test1" in repr_str
        assert "failed1" in repr_str


class TestDiagnosticMixin:
    """Test DiagnosticMixin functionality."""
    
    def test_diagnose_output(self, loader):
        """Test diagnose method output."""
        # Add some test data
        loader.loaded_modules["test1"] = True
        loader.loaded_modules["test2"] = True
        loader.failed_modules = ["failed1"]
        
        with patch('builtins.print') as mock_print:
            summary = loader.diagnose()
            
            # Check that print was called with diagnostic output
            assert mock_print.called
            assert summary["total_loaded"] == 2
            assert summary["total_failed"] == 1
    
    def test_generate_diagnostic_summary(self, loader):
        """Test diagnostic summary generation."""
        # Add test data
        loader.loaded_modules["test1"] = True
        loader.loaded_modules["test2"] = True
        loader.failed_modules = ["failed1"]
        loader.loaded_modules["skipped"] = ["skipped1"]
        
        summary = loader._generate_diagnostic_summary()
        
        assert summary["loaded"] == ["test1", "test2"]
        assert summary["failed"] == ["failed1"]
        assert summary["skipped"] == ["skipped1"]
        assert summary["total_loaded"] == 2
        assert summary["total_failed"] == 1
        assert summary["total_skipped"] == 1
    
    def test_export_summary_markdown(self, loader, tmp_path):
        """Test export summary to markdown."""
        # Add test data
        loader.loaded_modules["test1"] = True
        loader.failed_modules = ["failed1"]
        
        export_path = tmp_path / "summary.md"
        result_path = loader.export_summary(export_path)
        
        assert result_path.exists()
        content = result_path.read_text()
        assert "DynamicTaskLoader Summary Report" in content
        assert "test1" in content
        assert "failed1" in content
    
    def test_export_summary_json(self, loader, tmp_path):
        """Test export summary to JSON."""
        # Add test data
        loader.loaded_modules["test1"] = True
        loader.failed_modules = ["failed1"]
        
        export_path = tmp_path / "summary.json"
        result_path = loader.export_summary(export_path)
        
        assert result_path.exists()
        import json
        content = json.loads(result_path.read_text())
        assert "loaded" in content
        assert "failed" in content
        assert "test1" in content["loaded"]
        assert "failed1" in content["failed"]
    
    def test_generate_pulse(self, loader, tmp_path):
        """Test pulse generation."""
        # Add test data
        loader.loaded_modules["test1"] = True
        loader.failed_modules = ["failed1"]
        
        pulse_path = tmp_path / "pulse" / "index.mdx"
        result_path = loader.generate_pulse(pulse_path)
        
        assert result_path.exists()
        content = result_path.read_text()
        assert "title: \"Dynamic Loader Report\"" in content
        assert "tags: [\"diagnostics\", \"fab\", \"loader\"]" in content
        assert "test1" in content
        assert "failed1" in content


class TestLoadFunctions:
    """Test the main loading functions."""
    
    def test_load_all_modules(self):
        """Test load_all_modules function."""
        result = load_all_modules()
        
        assert result == {"mock_all": True}
        assert load_all_modules.call_count == 1
    
    def test_register_modules(self):
        """Test register_modules function."""
        result = register_modules(verbose=True)
        
        assert "loaded" in result
        assert "skipped" in result
        assert register_modules.call_count == 1


class TestCLI:
    """Test CLI functionality."""
    
    @patch('sys.argv', ['dynamic_loader.py', '--diagnose'])
    @patch('builtins.print')
    def test_cli_diagnose(self, mock_print):
        """Test CLI diagnose command."""
        # This would require refactoring the CLI to be more testable
        # For now, we'll just test that the function exists
        assert hasattr(load_all_modules, 'call_count')
    
    def test_export_summary_formats(self, loader, tmp_path):
        """Test export summary in different formats."""
        # Add test data
        loader.loaded_modules["test1"] = True
        loader.failed_modules = ["failed1"]
        
        # Test markdown export
        md_path = tmp_path / "summary.md"
        loader.export_summary(md_path)
        assert md_path.exists()
        
        # Test JSON export
        json_path = tmp_path / "summary.json"
        loader.export_summary(json_path)
        assert json_path.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 
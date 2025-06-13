import pytest

def test_agent0_basic_import():
    try:
        import agent0
    except ImportError:
        pytest.fail("agent0 module could not be imported.")

def test_agent0_has_main():
    import agent0
    assert hasattr(agent0, "main") or hasattr(agent0, "__version__"), "Expected 'main' or '__version__' attribute in agent0 module."

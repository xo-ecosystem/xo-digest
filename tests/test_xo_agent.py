import pytest

def test_xo_agent_importable():
    try:
        import xo_agent
    except ImportError:
        pytest.fail("Failed to import xo_agent module")

def test_xo_agent_has_main():
    import xo_agent
    assert hasattr(xo_agent, 'main'), "xo_agent should have a 'main' function"

def test_xo_agent_main_runs():
    import xo_agent
    try:
        xo_agent.main()
    except Exception as e:
        pytest.fail(f"xo_agent.main() raised an exception: {e}")
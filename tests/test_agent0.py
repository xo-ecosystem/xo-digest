import pytest

from xo_core import agent0


def test_agent0_basic_import():
    try:
        from xo_core import agent0
    except ImportError:
        pytest.fail("agent0 module could not be imported.")


def test_agent0_has_main():
    from xo_core import agent0

    assert hasattr(agent0, "main") or hasattr(
        agent0, "__version__"
    ), "agent0 module must have main or __version__"

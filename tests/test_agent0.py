import pytest

def test_agent0_basic_import():
    try:
        import agent0
        print("✅ agent0 module imported successfully.")
    except ImportError as e:
        pytest.fail(f"❌ Failed to import agent0 module: {e}")

def test_agent0_has_main():
    import agent0
    has_main = hasattr(agent0, "main")
    has_version = hasattr(agent0, "__version__")
    assert has_main or has_version, (
        "❌ agent0 module should have either a 'main' or '__version__' attribute."
    )
    print(f"✅ agent0 attributes present: main={has_main}, __version__={has_version}")

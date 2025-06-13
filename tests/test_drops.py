import pytest

def test_drops_module_importable():
    try:
        import drops
    except ImportError:
        pytest.fail("❌ Failed to import 'drops' module")

def test_drops_structure():
    import drops
    assert hasattr(drops, "__file__"), "❌ Module 'drops' should have a '__file__' attribute, but it's missing."

def test_drops_has_expected_attributes():
    import drops
    expected_attrs = ["upload_to_arweave", "bundle_metadata", "detect_drop_dir"]
    for attr in expected_attrs:
        assert hasattr(drops, attr), f"❌ Expected attribute '{attr}' not found in 'drops' module. Please check the implementation."


def test_upload_to_arweave_signature():
    import drops
    from inspect import signature

    sig = signature(drops.upload_to_arweave)
    assert "path" in sig.parameters, f"❌ 'upload_to_arweave' should accept 'path' as a parameter. Found parameters: {list(sig.parameters)}"


def test_bundle_metadata_signature():
    import drops
    from inspect import signature

    sig = signature(drops.bundle_metadata)
    assert "drop_path" in sig.parameters, f"❌ 'bundle_metadata' should accept 'drop_path' as a parameter. Found parameters: {list(sig.parameters)}"


def test_detect_drop_dir_behavior(tmp_path):
    import drops
    # Create dummy metadata to test detection logic
    drop_dir = tmp_path / "sample_drop"
    drop_dir.mkdir()
    (drop_dir / "drop_metadata.json").write_text('{"name": "test"}')

    result = drops.detect_drop_dir(drop_dir)
    assert result == drop_dir, f"❌ 'detect_drop_dir' did not return the expected path. Expected: {drop_dir}, Got: {result}"

from pathlib import Path

import pytest

from xo_core import drops


def test_drops_module_importable():
    try:
        import drops
    except ImportError:
        pytest.fail("❌ Failed to import 'drops' module")


def test_drops_structure():
    import drops

    assert hasattr(
        drops, "__file__"
    ), "❌ Module 'drops' should have a '__file__' attribute, but it's missing."


def test_drops_has_expected_attributes():
    expected_attrs = ["upload_to_arweave", "bundle_metadata", "detect_drop_dir"]
    for attr in expected_attrs:
        assert hasattr(
            drops, attr
        ), f"❌ Expected attribute '{attr}' not found in 'drops' module. Please check the implementation."


def test_upload_to_arweave_signature():
    from inspect import signature

    sig = signature(drops.upload_to_arweave)
    assert (
        sig.parameters.get("path") is not None
    ), "upload_to_arweave should have a 'path' parameter."


def test_bundle_metadata_signature():
    from inspect import signature

    sig = signature(drops.bundle_metadata)
    assert (
        sig.parameters.get("drop_path") is not None
    ), "bundle_metadata should have a 'drop_path' parameter."


def test_detect_drop_dir_behavior(tmp_path):
    drop_dir = tmp_path / "sample_drop"
    drop_dir.mkdir()
    (drop_dir / "drop_metadata.json").write_text('{"name": "test"}')
    result = drops.detect_drop_dir(drop_dir)
    assert (
        result == drop_dir
    ), "detect_drop_dir should return the path if it is a valid drop directory."

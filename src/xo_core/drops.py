"""
Drops module for XO Core.
"""

from pathlib import Path
from typing import Optional


def upload_to_arweave(path: str) -> str:
    """Upload a file to Arweave.

    Args:
        path: Path to the file to upload

    Returns:
        str: Transaction ID or URL
    """
    raise NotImplementedError("upload_to_arweave not implemented")


def bundle_metadata(drop_path: str) -> dict:
    """Bundle metadata for a drop.

    Args:
        drop_path: Path to the drop directory

    Returns:
        dict: Bundled metadata
    """
    raise NotImplementedError("bundle_metadata not implemented")


def detect_drop_dir(path: Path) -> Optional[Path]:
    """Detect if a directory is a valid drop directory.

    Args:
        path: Path to check

    Returns:
        Optional[Path]: Path to the drop directory if valid, None otherwise
    """
    if not path.is_dir():
        return None

    metadata_file = path / "drop_metadata.json"
    if metadata_file.exists():
        return path

    return None

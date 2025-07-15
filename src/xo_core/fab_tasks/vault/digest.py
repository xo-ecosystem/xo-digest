"""
Fallback vault digest module stub for testing purposes.
This provides mock implementations when the real vault digest module is not available.
"""

import logging
from pathlib import Path
from invoke import task

logger = logging.getLogger(__name__)

@task(help={"slug": "Pulse slug to update digest for"})
def update_digest(c, slug, **kwargs):
    """
    Mock digest update function for testing.
    
    Args:
        c: Fabric context
        slug: Pulse slug
        **kwargs: Additional arguments
    """
    logger.info(f"📒 Mock digest update: {slug}")
    
    # Create mock digest file
    digest_dir = Path("vault/.digest")
    digest_dir.mkdir(parents=True, exist_ok=True)
    
    digest_file = digest_dir / f"{slug}.digest"
    digest_content = f"""# Digest for {slug}

Generated: {Path(__file__).stat().st_mtime}
Status: mock_digest
"""
    digest_file.write_text(digest_content)
    
    return {
        "slug": slug,
        "digest_file": str(digest_file),
        "status": "updated"
    }

# Mock namespace for Fabric
from invoke import Collection

ns = Collection("digest")
ns.add_task(update_digest, name="update")

__all__ = ["update_digest", "ns"] 
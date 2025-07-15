"""
Fallback IPFS module stub for testing purposes.
This provides mock implementations when the real IPFS module is not available.
"""

import logging
from pathlib import Path
from invoke import task
import json
import markdown

logger = logging.getLogger(__name__)

@task(help={"path": "Path to file to pin"})
def pin_to_ipfs(c, path, **kwargs):
    """
    Mock IPFS pin function for testing.
    
    Args:
        c: Fabric context
        path: Path to file to pin
        **kwargs: Additional arguments
    """
    logger.info(f"🔗 Mock IPFS pin: {path}")
    return {
        "hash": "mock_ipfs_hash_1234567890abcdef",
        "size": Path(path).stat().st_size if Path(path).exists() else 0,
        "status": "pinned"
    }

@task(help={"path": "Path to file to upload", "format": "Output format: raw/json/markdown"})
def upload_to_ipfs(c, path, format="raw", **kwargs):
    logger.info(f"📤 Mock IPFS upload: {path}")
    result = {
        "cid": "mock_cid_1234567890abcdef",
        "url": f"https://ipfs.io/ipfs/mock_cid_1234567890abcdef",
        "size": Path(path).stat().st_size if Path(path).exists() else 0,
        "status": "uploaded"
    }

    if format == "json":
        print(json.dumps(result, indent=2))
    elif format == "markdown":
        print(f"[📦 View on IPFS]({result['url']})\n\n**CID:** `{result['cid']}`\n\n**Size:** `{result['size']} bytes`")
    else:
        print(result)

    return result


# Markdown preview task
@task(help={"path": "Path to .mdx file to render", "output": "Optional output .html file"})
def render_markdown_preview(c, path, output=None, **kwargs):
    """
    Converts a .mdx or .md file to an HTML preview.
    """
    logger.info(f"📝 Rendering Markdown preview: {path}")
    if not Path(path).exists():
        print(f"❌ File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    html = markdown.markdown(raw)

    if output:
        with open(output, "w", encoding="utf-8") as out:
            out.write(html)
        print(f"✅ Preview written to {output}")
    else:
        print(html)

# Mock namespace for Fabric
from invoke import Collection

ns = Collection("ipfs")
ns.add_task(pin_to_ipfs, name="pin")
ns.add_task(upload_to_ipfs, name="upload")
ns.add_task(render_markdown_preview, name="render")


# Generate .ipfs.mdx stub task
@task(help={"path": "Path to file to generate .ipfs.mdx for"})
def generate_ipfs_stub(c, path, **kwargs):
    """
    Generates a .ipfs.mdx stub for the given file with IPFS mock metadata.
    """
    logger.info(f"📄 Generating .ipfs.mdx stub for: {path}")
    result = upload_to_ipfs(c, path, format="raw")
    stub_path = Path(path).with_suffix(".ipfs.mdx")
    with open(stub_path, "w", encoding="utf-8") as f:
        f.write(f"""---
cid: {result['cid']}
url: {result['url']}
size: {result['size']}
status: {result['status']}
original: {path}
---

[📦 View IPFS file]({result['url']})
""")
    print(f"✅ .ipfs.mdx stub written to {stub_path}")

ns.add_task(generate_ipfs_stub, name="stub")

__all__ = ["pin_to_ipfs", "upload_to_ipfs", "render_markdown_preview", "generate_ipfs_stub", "ns"]
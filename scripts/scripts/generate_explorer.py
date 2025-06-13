import json
from pathlib import Path

SIGNED_DIR = Path("vault/.signed")
MANIFEST_PATH = SIGNED_DIR / "preview_manifest.json"
OUTPUT_HTML = SIGNED_DIR / "index.html"


def load_manifest():
    if not MANIFEST_PATH.exists():
        print("❌ preview_manifest.json not found.")
        return []
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def generate_html(manifest):
    head = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>XO Pulse Explorer</title>
    <style>
        body { font-family: sans-serif; padding: 2rem; background: #f4f4f4; }
        h1 { margin-bottom: 2rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 1rem; padding: 1rem; }
        .cid { font-size: 0.85rem; color: #666; word-break: break-all; }
        a { text-decoration: none; color: #0a66c2; }
    </style>
</head>
<body>
    <h1>🔍 XO Pulse Archive Explorer</h1>
"""

    body = ""
    for item in manifest:
        slug = item.get("slug", "unknown")
        cid = item.get("cid", "")
        body += f"""
        <div class="card">
            <strong>{slug}</strong><br>
            <div class="cid">CID: {cid}</div>
            <a href="https://arweave.net/{cid}" target="_blank">Arweave</a> |
            <a href="https://gateway.lighthouse.storage/ipfs/{cid}" target="_blank">Lighthouse</a> |
            <a href="{slug}.mdx" target="_blank">Local MDX</a>
            <br>
            <iframe
                src="https://gateway.lighthouse.storage/ipfs/{cid}"
                width="100%"
                height="400"
                loading="lazy"
                title="Preview of {slug}"
                aria-label="Preview of {slug}"
                style="margin-top: 1rem; border: 1px solid #ccc;">
            </iframe>
            <noscript>
                <p><a href="https://gateway.lighthouse.storage/ipfs/{cid}" target="_blank">View {slug} on Lighthouse (no preview)</a></p>
            </noscript>
        </div>
        """

    foot = "</body></html>"
    return head + body + foot


def main():
    manifest = load_manifest()
    if not manifest:
        return
    html = generate_html(manifest)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)
    print(f"✅ Explorer written to {OUTPUT_HTML}")


if __name__ == "__main__":
    main()

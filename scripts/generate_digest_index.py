# scripts/generate_digest_index.py
from datetime import datetime
from pathlib import Path

daily_dir = Path("scripts/xo-digest/daily")
output_path = Path("scripts/xo-digest/index.html")

entries = sorted(daily_dir.glob("*.md"), reverse=True)

html = [
    "<!DOCTYPE html>",
    "<html><head><meta charset='utf-8'><title>XO Digest</title></head><body>",
    "<h1>📬 XO Vault Digest</h1><ul>",
]

for entry in entries:
    date = entry.stem.split(".")[0]  # e.g. 2025-06-25
    html.append(f'<li><a href="daily/{entry.name}">{date}</a></li>')

html += ["</ul></body></html>"]

output_path.write_text("\n".join(html), encoding="utf-8")
print(f"✅ index.html generated with {len(entries)} entries")

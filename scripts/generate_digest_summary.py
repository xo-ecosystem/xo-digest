import re
import sys
from datetime import datetime
from pathlib import Path

import markdown

input_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
is_slim = "--slim" in sys.argv


def autolink_pulse_and_drop(line):
    return re.sub(r"([a-z0-9\-_]+\.mdx)", r"[/pulses/\1](\/pulses/\1)", line)


def link_arweave_tx(line):
    return re.sub(
        r"(txid: *([a-zA-Z0-9\-_]+))", r"[txid:\2](https://arweave.net/\2)", line
    )


def filter_and_format(lines, slim=False):
    if not slim:
        return lines
    return [line for line in lines if any(t in line for t in ["✅", "❌", "⚠️"])]


def format_digest(lines):
    out = [
        "# 🧾 XO CI Digest Summary\n",
        f"_Generated on {datetime.utcnow().isoformat()} UTC_\n",
        "---\n",
    ]
    for line in lines:
        line = autolink_pulse_and_drop(line)
        line = link_arweave_tx(line)
        out.append(line)
    return out


if not input_path.exists():
    print(f"❌ Input file not found: {input_path}")
    sys.exit(1)

lines = input_path.read_text().splitlines()
lines = filter_and_format(lines, is_slim)
summary = format_digest(lines)

output_path.write_text("\n".join(summary))
print(f"✅ Digest summary written to: {output_path}")

html_output_path = Path("vault/daily/index.html")
html = markdown.markdown("\n".join(summary), extensions=["extra", "toc"])
html_output_path.write_text(html)
print(f"🌐 Digest HTML view written to: {html_output_path}")

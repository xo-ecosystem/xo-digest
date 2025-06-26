#!/usr/bin/env python3

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SIGNED_DIR = Path(".signed")
INDEX_PATH = SIGNED_DIR / "index.html"

grouped_entries = defaultdict(list)
for file in sorted(SIGNED_DIR.glob("*.json")):
    try:
        data = json.loads(file.read_text())
        # Validation: skip if missing or invalid slug or signed_at
        slug = data.get("slug")
        signed_at = data.get("signed_at")
        if (
            not isinstance(slug, str)
            or not slug.strip()
            or not isinstance(signed_at, str)
            or not signed_at.strip()
        ):
            print(f"⚠️ Skipping invalid: {file.name}")
            continue
        slug = slug
        score = data.get("importance_score", 0)
        trigger = data.get("trigger_source", "unknown")
        month = "Unknown"
        try:
            dt = datetime.fromisoformat(signed_at.replace("Z", ""))
            month = dt.strftime("%B %Y")
        except:
            pass
        grouped_entries[month].append((slug, score, trigger, signed_at))
    except Exception as e:
        print(f"⚠️ Failed to load {file.name}: {e}")

# Track all slugs and find unsigned ones
all_mdx_slugs = sorted([p.stem for p in Path("content/pulses").glob("*.mdx")])
signed_slugs = {slug for entries in grouped_entries.values() for slug, *_ in entries}
unsigned_slugs = [slug for slug in all_mdx_slugs if slug not in signed_slugs]

# Create auto-comments for signed pulses if missing
comments_dir = Path(".comments")
comments_dir.mkdir(exist_ok=True)
for slug in signed_slugs:
    comment_path = comments_dir / f"{slug}.comments.mdx"
    if not comment_path.exists():
        comment_path.write_text(
            f"<!-- Auto-comment for {slug} -->\n💬 This pulse was signed and added to the explorer.\n"
        )

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>XO Signed Pulse Explorer</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
  <style>
    body {
      font-family: system-ui, sans-serif;
      padding: 2rem;
      background: #fcfcfc;
      color: #222;
    }
    h1 {
      margin-bottom: 1rem;
      color: #154;
      font-size: 1.8rem;
      border-bottom: 2px solid #ccc;
      padding-bottom: 0.5rem;
    }
    table {
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 2rem;
    }
    th, td {
      background-color: white !important;
      color: #111 !important;
      padding: 0.6rem;
      border: 1px solid #ddd;
      text-align: left;
    }
    tr:hover {
      background-color: #f0f8ff !important;
    }
    a {
      text-decoration: none;
      color: #1a73e8;
    }
  </style>
</head>
<body>
<!-- explorer ready -->
  <h1>🔏 Signed Pulses</h1>
"""

for month in sorted(grouped_entries.keys(), reverse=True):
    html += f"<h2>📅 {month}</h2><table><tr><th>Slug</th><th>Score</th><th>Trigger</th><th>Signed At</th></tr>"
    for slug, score, trigger, signed_at in grouped_entries[month]:
        html += f"<tr><td><a href='../content/pulses/{slug}.mdx'>{slug}</a></td><td>{score:.2f} <div style='background:#0a0;width:{score*100:.0f}px;height:6px;display:inline-block;margin-left:8px;'></div></td><td>{trigger}</td><td>{signed_at}</td></tr>\n"
    html += "</table>"

# Append unsigned pulses section before closing </body>
if unsigned_slugs:
    html += "<h2>🚫 Unsigned Pulses</h2><ul>"
    for slug in unsigned_slugs:
        html += f"<li>{slug}</li>"
    html += "</ul>"

html += """
<div style="margin-top:1rem;">
  <label>🔍 Min score: <input type="number" id="minScore" value="0.0" step="0.01" style="width:4em;"></label>
  <label style="margin-left:2em;">🎯 Trigger:
    <select id="triggerFilter">
      <option value="">(all)</option>
      <option value="pulse.publish">pulse.publish</option>
      <option value="emoji.reaction">emoji.reaction</option>
      <option value="comment.added">comment.added</option>
      <option value="agent0.trigger">agent0.trigger</option>
      <option value="webhook.notify">webhook.notify</option>
    </select>
  </label>
  <button onclick="applyFilters()">Apply</button>
  <button onclick="resetFilters()">Reset</button>
  <span id="visibleCount" style="margin-left:2em;"></span>
  <button onclick="downloadFiltered()">⬇️ Export filtered CSV</button>
</div>

<script>
function resetFilters() {
  document.getElementById("minScore").value = "0.0";
  document.getElementById("triggerFilter").value = "";
  applyFilters();
}

function updateVisibleCount() {
  let count = 0;
  document.querySelectorAll("table tr").forEach((row, idx) => {
    if (idx === 0) return;
    if (row.style.display !== "none") count++;
  });
  document.getElementById("visibleCount").textContent = `🧮 Visible: ${count}`;
}

function applyFilters() {
  const minScore = parseFloat(document.getElementById("minScore").value);
  const trigger = document.getElementById("triggerFilter").value;
  document.querySelectorAll("table tr").forEach((row, idx) => {
    if (idx === 0) return;
    const score = parseFloat(row.cells[1].textContent);
    const rowTrigger = row.cells[2].textContent.trim();
    const show = (!isNaN(score) && score >= minScore) && (!trigger || rowTrigger === trigger);
    row.style.display = show ? "" : "none";
  });
  updateVisibleCount();
}

function downloadFiltered() {
  let csv = "Slug,Score,Trigger,Signed At\\n";
  document.querySelectorAll("table tr").forEach((row, idx) => {
    if (idx === 0 || row.style.display === "none") return;
    const cells = Array.from(row.cells).map(cell => cell.textContent.trim().replace(/\\n/g, ""));
    csv += cells.join(",") + "\\n";
  });
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "filtered_signed_data.csv";
  a.click();
  URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll("th").forEach((th, index) => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => {
      const table = th.closest("table");
      const rows = Array.from(table.querySelectorAll("tr")).slice(1);
      const sorted = rows.sort((a, b) => {
        const aText = a.cells[index].textContent.trim();
        const bText = b.cells[index].textContent.trim();
        return isNaN(aText - bText) ? aText.localeCompare(bText) : bText - aText;
      });
      sorted.forEach(row => table.appendChild(row));
    });
  });
  // Initialize count on load
  applyFilters();
});
</script>
"""
html += """
</body>
</html>
"""

INDEX_PATH.write_text(html)
print(f"✅ Explorer written to {INDEX_PATH}")
# Also write stats.json
stats = {
    "total_signed": sum(len(entries) for entries in grouped_entries.values()),
    "top_3_by_score": sorted(
        [entry for entries in grouped_entries.values() for entry in entries],
        key=lambda x: -x[1],
    )[:3],
}
(Path(".signed") / "stats.json").write_text(json.dumps(stats, indent=2))
print("📊 stats.json generated.")

import csv

csv_path = SIGNED_DIR / "signed_data.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Slug", "Score", "Trigger", "Signed At"])
    for entries in grouped_entries.values():
        for slug, score, trigger, signed_at in entries:
            writer.writerow([slug, score, trigger, signed_at])
print("📑 signed_data.csv exported.")

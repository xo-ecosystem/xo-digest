/* Build a minimal Digest HTML from data/pulse/*.json */
import fs from "fs";
import path from "path";

const ROOT = process.cwd();
const pulseDir = path.join(ROOT, "data", "pulse");
const outDir = path.join(ROOT, "out", "digest");
fs.mkdirSync(outDir, { recursive: true });

const files = fs.existsSync(pulseDir) ? fs.readdirSync(pulseDir).filter(f=>f.endsWith(".json")) : [];
const items = files.map(f => {
  try { return JSON.parse(fs.readFileSync(path.join(pulseDir, f), "utf8")); }
  catch { return null; }
}).filter(Boolean).sort((a,b)=> String(b.date).localeCompare(String(a.date)));

const html = `<!doctype html>
<html><head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>XO Digest</title>
  <style>
    body{font-family: ui-sans-serif, system-ui, -apple-system; padding:24px; max-width:900px; margin:0 auto;}
    .item{border:1px solid #eee; border-radius:12px; padding:16px; margin:12px 0;}
    .meta{font-size:12px; opacity:.7}
    .links a{font-size:12px; margin-right:8px}
  </style>
</head><body>
  <h1>XO Digest</h1>
  <p class="meta">Entries: ${items.length}</p>
  ${items.map(it => `
    <div class="item">
      <div class="meta">${it.date || ""} · ${it.id || ""}</div>
      <h3>${it.title || ""}</h3>
      <p>${it.summary || ""}</p>
      <div class="links">
        ${(it.links||[]).map((l)=>`<a href="${l.href}" target="_blank" rel="noreferrer">${l.label||l.href}</a>`).join("")}
      </div>
    </div>
  `).join("")}
</body></html>`;

fs.writeFileSync(path.join(outDir, "index.html"), html, "utf8");
console.log("Built:", path.join(outDir, "index.html"));

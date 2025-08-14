from pathlib import Path
from typing import Optional


def render_embed(
    slug: str, run_id: Optional[str] = None, signed_url: Optional[str] = None
) -> str:
    title = "Join the Trust Continuum"
    desc = "Obsolete the stolen asset economy. XO Ledger + Aether Relayer."
    visual = Path(__file__).parent / "trust_continuum" / "visual.png"
    link = signed_url or (f"/vault/decoded/{run_id}/index.html" if run_id else "#")
    img_src = visual.as_posix()
    return f"""
<div style='font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0b0f14;color:#e6edf3;border:1px solid #1f2937;border-radius:12px;overflow:hidden'>
  <div style='display:flex;gap:16px;align-items:center;padding:16px;background:#111827'>
    <img src='{img_src}' alt='Trust Continuum' style='width:96px;height:96px;object-fit:cover;border-radius:8px;border:1px solid #1f2937' />
    <div>
      <div style='font-size:18px;font-weight:600'>{title}</div>
      <div style='opacity:.85;margin-top:4px'>{desc}</div>
      <div style='margin-top:12px'>
        <a href='{link}' style='background:#2563eb;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none'>Open Report</a>
      </div>
    </div>
  </div>
</div>
"""

from __future__ import annotations
import os, re, json, base64, binascii, gzip, io, zipfile, tarfile, hashlib, mimetypes, uuid, html
from dataclasses import dataclass, asdict
from typing import Any, Optional
from pathlib import Path

DECODE_MAX_MB = int(os.getenv("XO_DECODE_MAX_MB", "25"))
OUTPUT_BASE = Path(os.path.expanduser("~/.config/xo-core/decoded")).resolve()
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

ALLOWED_MIMES = {
    "text/plain",
    "application/json",
    "application/x-yaml",
    "text/markdown",
    "application/zip",
    "application/gzip",
    "application/x-tar",
    "image/png",
    "image/jpeg",
    "image/webp",
}


def get_trust_state(sha256: str, context: str = "manual") -> dict:
    try:
        from xo_core.vault.chain import get_trust_state as _gts  # type: ignore

        return _gts(sha256=sha256, context=context)
    except Exception:
        return {"state": "unknown", "sha256": sha256, "context": context}


@dataclass
class DecodeArtifact:
    path: str
    mime: str | None = None
    size: int | None = None
    sha256: str | None = None
    redacted: bool = False


@dataclass
class DecodeResult:
    ok: bool
    run_id: str
    summary: str
    artifacts: list[DecodeArtifact]
    risk: str
    trust: dict[str, Any]
    html_report: str | None = None
    base_dir: str | None = None
    index_route: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def _write_bytes(dst: Path, data: bytes) -> DecodeArtifact:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    h = hashlib.sha256(data).hexdigest()
    mime = mimetypes.guess_type(dst.name)[0]
    return DecodeArtifact(path=str(dst), mime=mime, size=len(data), sha256=h)


def _within_limit(data: bytes) -> None:
    if len(data) > DECODE_MAX_MB * 1024 * 1024:
        raise ValueError(f"Input exceeds {DECODE_MAX_MB}MB limit")


def _maybe_from_str_or_file(input: Any) -> tuple[bytes, str]:
    # input can be {'filename','bytes'} OR path OR 'str://...'
    if isinstance(input, dict) and "bytes" in input:
        data = input["bytes"]
        _within_limit(data)
        name = input.get("filename") or "upload.bin"
        name = Path(name).name  # sanitize
        return data, name
    if isinstance(input, str):
        if input.startswith("str://"):
            s = input[len("str://") :]
            b = s.encode("utf-8")
            _within_limit(b)
            return b, "inline.txt"
        p = Path(input)
        data = p.read_bytes()
        _within_limit(data)
        return data, p.name
    raise ValueError("Unsupported input type")


def _try_base64(raw: bytes) -> Optional[bytes]:
    s = raw.strip()
    if re.fullmatch(rb"[A-Za-z0-9+/=\s]{16,}", s):
        try:
            return base64.b64decode(s, validate=True)
        except binascii.Error:
            return None
    return None


def _try_json(raw: bytes) -> Optional[bytes]:
    try:
        obj = json.loads(raw.decode("utf-8"))
        return json.dumps(obj, indent=2).encode()
    except Exception:
        return None


def _try_yaml(raw: bytes) -> Optional[bytes]:
    try:
        import yaml

        obj = yaml.safe_load(raw.decode("utf-8"))
        return yaml.safe_dump(obj, sort_keys=False).encode()
    except Exception:
        return None


def _try_compressed(raw: bytes) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    # gzip
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
            out.append(("decompressed.gz", gz.read()))
    except Exception:
        pass
    # zip
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
        for name in zf.namelist():
            safe_name = Path(name).name or "file.bin"
            try:
                data = zf.read(name)
            except KeyError:
                continue
            out.append((f"zip/{safe_name}", data))
    except Exception:
        pass
    # tar
    try:
        tf = tarfile.open(fileobj=io.BytesIO(raw))
        for m in tf.getmembers():
            if m.isfile() and m.size <= DECODE_MAX_MB * 1024 * 1024:
                fobj = tf.extractfile(m)
                if fobj:
                    safe_name = Path(m.name).name or "file.bin"
                    out.append((f"tar/{safe_name}", fobj.read()))
    except Exception:
        pass
    return out


def _scan_for_secrets(b: bytes) -> bool:
    text = b.decode("utf-8", errors="ignore")
    hot = re.search(r"(AKIA[0-9A-Z]{16}|SECRET|PRIVATE KEY|TOKEN|PASSWORD)", text, re.I)
    return bool(hot)


def _redact_preview(b: bytes) -> bytes:
    t = b.decode("utf-8", errors="ignore")
    t = re.sub(r"([A-Za-z0-9_\-]{16,})", "__REDACTED__", t)
    return t.encode()


def _write_html_report(result: DecodeResult) -> str:
    run_dir = Path(result.base_dir) if result.base_dir else OUTPUT_BASE / result.run_id
    html_path = run_dir / "index.html"

    def esc(s: object) -> str:
        return html.escape(str(s))

    def rel_path(p: str) -> str:
        try:
            return str(Path(p).resolve().relative_to(run_dir.resolve()))
        except Exception:
            return Path(p).name

    # Build preview map for redacted previews
    preview_set = set()
    for a in result.artifacts:
        if a.path.endswith(".preview.txt"):
            try:
                preview_set.add(
                    str(Path(a.path).resolve().relative_to(run_dir.resolve()))
                )
            except Exception:
                pass

    rows: list[str] = []
    for art in result.artifacts:
        if art.path.endswith(".preview.txt"):
            continue
        relp = rel_path(art.path)
        fname = esc(relp)
        mime = esc(art.mime or "")
        size = esc(f"{(art.size or 0)/1024:.1f} KB")
        sha = esc(art.sha256 or "")
        risk_badge = (
            '<span style="color:red;">HIGH</span>' if result.risk == "high" else "low"
        )
        preview_link = ""
        if Path(art.path).suffix.lower() in (".txt", ".json", ".yaml", ".yml"):
            preview_link = f'<a href="{fname}">View</a>'
        pr = str(Path(relp).with_suffix(".preview.txt"))
        if pr in preview_set:
            preview_link = f'<a href="{esc(pr)}">Preview</a>'
        rows.append(
            f"<tr><td>{fname}</td><td>{mime}</td><td>{size}</td><td>{sha}</td><td>{risk_badge}</td><td>{preview_link}</td></tr>"
        )

    overall_risk_html = (
        '<span style="color:red;">HIGH</span>' if result.risk == "high" else "low"
    )
    rows_html = "".join(rows)
    html_content = (
        "<!DOCTYPE html>\n"
        '<html lang="en"><head><meta charset="utf-8">\n'
        f"<title>agent.decode — {esc(result.run_id)}</title>\n"
        "<style>\n"
        "body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; padding: 24px; background:#0b0f14; color:#e6edf3; }\n"
        "h1, h2 { margin: 0 0 12px 0; }\n"
        ".card { background:#111827; border:1px solid #1f2937; border-radius:12px; padding:16px; margin: 16px 0; }\n"
        "table { border-collapse: collapse; width:100%; }\n"
        "td, th { border:1px solid #374151; padding:8px; text-align:left; }\n"
        "th { background:#1f2937; }\n"
        ".badge { padding: 2px 6px; border-radius:6px; background:#374151; }\n"
        "</style></head>\n"
        "<body>\n"
        f'  <h1>Decode Report — <span class="badge">{esc(result.run_id)}</span></h1>\n'
        '  <div class="card">\n'
        f"    <p><strong>Summary:</strong> {esc(result.summary)}</p>\n"
        f"    <p><strong>Risk:</strong> {overall_risk_html}</p>\n"
        f"    <p><strong>Trust:</strong> {esc(result.trust.get('state', 'unknown'))}</p>\n"
        "  </div>\n"
        '  <div class="card">\n'
        "    <h2>Artifacts</h2>\n"
        "    <table>\n"
        "      <thead><tr><th>File</th><th>Mime</th><th>Size</th><th>SHA256</th><th>Risk</th><th>Preview</th></tr></thead>\n"
        "      <tbody>\n"
        f"        {rows_html}\n"
        "      </tbody>\n"
        "    </table>\n"
        "  </div>\n"
        "</body></html>"
    )
    html_path.write_text(html_content, encoding="utf-8")
    return str(html_path)


def decode_entrypoint(
    input: Any, context: str = "manual", run_id: str | None = None
) -> DecodeResult:
    run_id = run_id or uuid.uuid4().hex[:12]
    run_dir = OUTPUT_BASE / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    raw, name = _maybe_from_str_or_file(input)
    artifacts: list[DecodeArtifact] = []

    # 1) Always store original (never commit)
    orig = _write_bytes(run_dir / f"input/{name}", raw)
    artifacts.append(orig)

    # 2) Strategy chain
    decoded: list[tuple[str, bytes]] = []
    b64 = _try_base64(raw)
    if b64:
        decoded.append(("decoded/base64.bin", b64))
    jsn = _try_json(raw)
    if jsn:
        decoded.append(("normalized/pretty.json", jsn))
    yml = _try_yaml(raw)
    if yml:
        decoded.append(("normalized/pretty.yaml", yml))
    for outname, body in _try_compressed(raw):
        decoded.append((f"expanded/{outname}", body))

    # 3) Persist decoded and make redacted previews if needed
    high_risk = False
    for outname, body in decoded:
        art = _write_bytes(run_dir / outname, body)
        if _scan_for_secrets(body):
            high_risk = True
            prev = _redact_preview(body)
            prt = _write_bytes(
                run_dir / (Path(outname).with_suffix(".preview.txt")), prev
            )
            prt.redacted = True
            artifacts.append(prt)
        artifacts.append(art)

    # 4) Trust annotation
    trust = get_trust_state(sha256=orig.sha256 or "", context=context)

    summary = (
        f"Decoded {len(decoded)} item(s) from {name}"
        if decoded
        else "No obvious decodings; stored original."
    )
    risk = "high" if high_risk else "low"

    result = DecodeResult(
        ok=True,
        run_id=run_id,
        summary=summary,
        artifacts=artifacts,
        risk=risk,
        trust=trust,
        base_dir=str(run_dir),
    )
    result.html_report = _write_html_report(result)
    result.index_route = f"/vault/decoded/{run_id}/index.html"
    return result

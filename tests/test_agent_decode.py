from xo_core.agent.decoders.runner import decode_entrypoint
import base64
from pathlib import Path


def test_decode_base64_roundtrip():
    s = base64.b64encode(b'{"ok":true}').decode()
    res = decode_entrypoint(input="str://" + s)
    assert res.ok
    assert "Decoded" in res.summary or res.summary.startswith("No obvious")
    assert any(
        a.path.endswith("pretty.json") or a.path.endswith("base64.bin")
        for a in res.artifacts
    )


def test_decode_json_pretty():
    res = decode_entrypoint(input='str://{"x":1}')
    assert any(a.path.endswith("pretty.json") for a in res.artifacts)


def test_html_report_created():
    res = decode_entrypoint(input='str://{"x":1}')
    assert res.html_report and Path(res.html_report).exists()
    content = Path(res.html_report).read_text()
    assert "<html" in content.lower()
    assert res.run_id in content

import os


def test_dev_signer_roundtrip(tmp_path, monkeypatch):
    keyf = tmp_path / "dev.json"
    keyf.write_text('{"private_key":"0x' + "11" * 32 + '"}')
    os.chmod(keyf, 0o600)
    monkeypatch.setenv("XO_SIGNER_FILE", str(keyf))
    monkeypatch.setenv("XO_SIGNER_BACKEND", "dev-file")

    from xo_core.crypto.signer import get_signer

    s = get_signer()
    out = s.sign_message(b"hello")
    assert out["signature"].startswith("0x")
    assert out["message_sha256"]

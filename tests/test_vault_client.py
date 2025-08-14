def test_env_fallback(monkeypatch):
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    monkeypatch.setenv("FOO_SECRET", "bar")
    from xo_core.vault.client import get_secret

    assert get_secret("FOO_SECRET") == "bar"

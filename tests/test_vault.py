import pytest
from vault import sign_all

def test_sign_all_executes_without_error(monkeypatch):
    class MockResponse:
        status_code = 200
        text = "✅ Signed all vault entries"

    def mock_post(url, *args, **kwargs):
        assert url.endswith("/vault/sign-all"), f"Unexpected URL: {url}"
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)
    output = sign_all()
    print(f"[TEST OUTPUT] {output}")
    assert "✅" in output, "Expected success emoji not found"
    assert "vault entries" in output, "Expected 'vault entries' in output"

def test_sign_all_handles_error(monkeypatch):
    class MockErrorResponse:
        status_code = 500
        text = "❌ Server error"

    def mock_post(url, *args, **kwargs):
        return MockErrorResponse()

    monkeypatch.setattr("requests.post", mock_post)
    output = sign_all()
    print(f"[TEST OUTPUT] {output}")
    assert "❌" in output or "error" in output.lower(), "Error handling failed or unexpected output"

    # Simulate a timeout and check fallback output
    import requests
    def mock_post_timeout(url, *args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out")

    monkeypatch.setattr("requests.post", mock_post_timeout)
    output = sign_all()
    print(f"[TEST OUTPUT] {output}")
    assert "timeout" in output.lower() or "error" in output.lower(), "Timeout not handled properly"

def test_sign_all_unexpected_url(monkeypatch):
    class MockResponse:
        status_code = 200
        text = "✅ Signed"

    def mock_post(url, *args, **kwargs):
        assert not url.endswith("/unexpected"), "URL should not end with /unexpected"
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)
    output = sign_all()
    print(f"[TEST OUTPUT] {output}")
    assert "✅" in output, "Expected success emoji not found in fallback case"

def test_sign_all_timeout_exception(monkeypatch):
    import requests

    def mock_post(url, *args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out")

    monkeypatch.setattr("requests.post", mock_post)
    output = sign_all()
    print(f"[TEST OUTPUT] {output}")
    assert "timeout" in output.lower() or "error" in output.lower(), "Timeout not handled properly"
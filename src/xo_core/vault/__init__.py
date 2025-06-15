# vault/__init__.py
import requests


def sign_all(url: str = "http://localhost:8000/sign-all") -> str:
    """Ping the local signer service and return a status message."""
    try:
        r = requests.post(url, timeout=5)
        if r.status_code == 200:
            return "✅ signed all vault entries"
        return f"❌ error {r.status_code}"
    except requests.exceptions.Timeout:
        return "❌ timeout contacting signer"

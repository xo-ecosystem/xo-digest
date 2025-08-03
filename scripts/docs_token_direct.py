#!/usr/bin/env python3
"""
Direct execution of docs.token functionality without fabric runtime config issues.
Workaround for July Recovery fabric config conflict.
"""

import os
import sys
import time
import jwt
import requests
from pathlib import Path
from dotenv import set_key

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def docs_token():
    """Fetch GitHub App Installation Token and export to .env.local"""
    app_id = os.getenv("XO_DOCS_APP_ID")
    installation_id = os.getenv("XO_DOCS_INSTALLATION_ID")
    pem_path = os.path.expanduser(os.getenv("XO_DOCS_PRIVATE_KEY_PATH", ""))

    if not app_id or not installation_id or not pem_path:
        print("❌ Missing XO_DOCS env variables:")
        print(f"   - XO_DOCS_APP_ID: {'✅' if app_id else '❌'}")
        print(f"   - XO_DOCS_INSTALLATION_ID: {'✅' if installation_id else '❌'}")
        print(f"   - XO_DOCS_PRIVATE_KEY_PATH: {'✅' if pem_path else '❌'}")
        return False

    try:
        private_key = Path(pem_path).read_text()
        now = int(time.time())
        payload = {"iat": now, "exp": now + 600, "iss": int(app_id)}
        jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
        }
        url = (
            f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        )
        res = requests.post(url, headers=headers)

        if res.status_code != 201:
            print(f"❌ Token fetch failed: {res.status_code} → {res.text}")
            return False

        token = res.json()["token"]
        print(f"✅ Token fetched → {token[:8]}...")

        # Export to .env.local for mkdocs deploy
        dotenv_path = Path(".env.local")
        dotenv_path.touch(exist_ok=True)
        set_key(dotenv_path, "GH_TOKEN", token)
        print(f"📦 Token written to .env.local as GH_TOKEN")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = docs_token()
    sys.exit(0 if success else 1)

import jwt
import time
import requests
import os


def fetch_github_app_token():
    app_id = os.getenv("XO_DOCS_APP_ID")
    installation_id = os.getenv("XO_DOCS_INSTALLATION_ID")
    private_key_path = os.getenv("XO_DOCS_PRIVATE_KEY_PATH")

    with open(private_key_path, "r") as f:
        private_key = f.read()

    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id,
    }

    jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)

    if response.ok:
        return response.json().get("token")
    else:
        print(response.status_code, response.json())
        return None

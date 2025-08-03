#!/usr/bin/env python3

import os, jwt, time, requests
from pathlib import Path

app_id = os.getenv("XO_DOCS_APP_ID")
installation_id = os.getenv("XO_DOCS_INSTALLATION_ID")
pem_path = os.path.expanduser(os.getenv("XO_DOCS_PRIVATE_KEY_PATH"))

if not app_id or not installation_id:
    raise EnvironmentError("Missing XO_DOCS_APP_ID or XO_DOCS_INSTALLATION_ID")

with open(pem_path, "r") as f:
    private_key = f.read()

now = int(time.time())
payload = {"iat": now, "exp": now + 600, "iss": int(app_id)}
jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github+json",
}
url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
res = requests.post(url, headers=headers)
print(res.status_code)
print(res.json())

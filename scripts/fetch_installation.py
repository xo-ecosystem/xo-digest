#!/usr/bin/env python3

import os
import jwt
import time
import requests
from pathlib import Path

# Load values from env
app_id = os.getenv("XO_DOCS_APP_ID")
pem_path = os.path.expanduser(
    os.getenv("XO_DOCS_PRIVATE_KEY_PATH")
    or "~/xo-secrets/xo-docs-bot.2025-08-01.private-key.pem"
)

if not app_id:
    raise EnvironmentError("Missing XO_DOCS_APP_ID environment variable")
if not Path(pem_path).exists():
    raise FileNotFoundError(f"Private key not found at: {pem_path}")

# Generate JWT
with open(pem_path, "r") as f:
    private_key = f.read()

now = int(time.time())
payload = {
    "iat": now,
    "exp": now + (10 * 60),
    "iss": int(app_id),
}
jwt_token = jwt.encode(payload, private_key, algorithm="RS256")

# Make GitHub App installation request
headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Accept": "application/vnd.github+json",
}
response = requests.get("https://api.github.com/app/installations", headers=headers)

print(response.status_code)
print(response.json())

#!/usr/bin/env python3
import jwt
import time
import os

app_id = "1713757"

pem_path = os.path.expanduser("~/xo-secrets/xo-docs-bot.2025-08-01.private-key.pem")


with open(pem_path, "r") as f:
    private_key = f.read()

now = int(time.time())
payload = {"iat": now, "exp": now + (10 * 60), "iss": app_id}

encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
print(encoded_jwt)

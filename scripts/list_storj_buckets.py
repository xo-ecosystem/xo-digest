# scripts/list_storj_buckets.py
from uplink_python import uplink

client = uplink.Client()
project = client.open_project("satellite-url", "api-key", "encryption-passphrase")

for bucket in project.list_buckets():
    print("🪣", bucket.name)

#!/usr/bin/env python3
"""
Verify a daily audit prefix:
 - fetch manifest.json (or manifest.root + .sig) from Storj S3
 - recompute Merkle root from listed objects
 - ask Vault Transit to verify the signature

Usage:
  python3 scripts/audit_verify.py --prefix audit/2025-08-13
"""
import argparse, base64, hashlib, json, os, sys
import boto3, requests


def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(f"missing env {name}")
    return v


def get_manifest(s3, bucket, prefix):
    try:
        obj = s3.get_object(Bucket=bucket, Key=f"{prefix}/manifest.json")
        return json.loads(obj["Body"].read().decode())
    except s3.exceptions.NoSuchKey:
        raise SystemExit("manifest.json not found")


def merkle_root(hex_hashes):
    if not hex_hashes:
        return hashlib.sha256(b"").hexdigest()
    layer = [bytes.fromhex(h) for h in sorted(hex_hashes)]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()


def transit_verify(vault_addr, token, key_name, root_hex, signature):
    url = f"{vault_addr.rstrip('/')}/v1/transit/verify/{key_name}"
    digest_b64 = base64.b64encode(bytes.fromhex(root_hex)).decode()
    r = requests.post(
        url,
        headers={"X-Vault-Token": token},
        json={
            "hash_algorithm": "sha2-256",
            "prehashed": True,
            "input": digest_b64,
            "signature": signature,
        },
        timeout=20,
    )
    if r.status_code != 200:
        raise SystemExit(f"transit verify error {r.status_code}: {r.text}")
    return r.json()["data"]["valid"], r.json()["data"].get("key_version")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--prefix", required=True, help="S3 prefix to verify, e.g., audit/2025-08-13"
    )
    args = ap.parse_args()

    ak = env("XO_STORJ_S3_ACCESS_KEY_ID")
    sk = env("XO_STORJ_S3_SECRET_ACCESS_KEY")
    ep = env("XO_STORJ_S3_ENDPOINT")
    bucket = env("XO_STORJ_S3_BUCKET")
    s3 = boto3.client(
        "s3", aws_access_key_id=ak, aws_secret_access_key=sk, endpoint_url=ep
    )

    manifest = get_manifest(s3, bucket, args.prefix)
    leafs = [o["sha256"] for o in manifest["objects"]]
    recomputed = merkle_root(leafs)
    if recomputed != manifest["merkle_root"]:
        raise SystemExit(
            f"❌ merkle mismatch: recomputed={recomputed} manifest={manifest['merkle_root']}"
        )

    vault_addr = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    token = (
        os.environ.get("VAULT_TOKEN")
        or open(os.path.expanduser("~/.config/xo-vault/dev_token")).read().strip()
    )
    sig = manifest["signature"]["signature"]
    key = manifest["signature"]["key"]

    valid, kver = transit_verify(vault_addr, token, key, recomputed, sig)
    if not valid:
        raise SystemExit("❌ signature invalid")
    print(f"✅ verified prefix s3://{bucket}/{args.prefix}")
    print(f"    objects: {len(leafs)}")
    print(f"    merkle_root: {recomputed}")
    print(f"    key: {key} v{kver}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Diff two audit manifests (S3 or local files).
Usage:
  python3 scripts/audit_diff.py --a audit/2025-08-12 --b audit/2025-08-13
"""
import argparse, json, os, sys
import boto3


def env(n):
    v = os.environ.get(n)
    if not v:
        raise SystemExit(f"missing env {n}")
    return v


def load_manifest(s3, bucket, path):
    if path.startswith("audit/"):
        obj = s3.get_object(Bucket=bucket, Key=f"{path}/manifest.json")
        return json.loads(obj["Body"].read().decode())
    else:
        with open(path) as f:
            return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    args = ap.parse_args()

    ak = env("XO_STORJ_S3_ACCESS_KEY_ID")
    sk = env("XO_STORJ_S3_SECRET_ACCESS_KEY")
    ep = env("XO_STORJ_S3_ENDPOINT")
    bucket = env("XO_STORJ_S3_BUCKET")
    s3 = boto3.client(
        "s3", aws_access_key_id=ak, aws_secret_access_key=sk, endpoint_url=ep
    )

    A = load_manifest(s3, bucket, args.a)
    B = load_manifest(s3, bucket, args.b)
    a_set = {(o["key"], o["sha256"], o["size"]) for o in A["objects"]}
    b_set = {(o["key"], o["sha256"], o["size"]) for o in B["objects"]}
    added = b_set - a_set
    removed = a_set - b_set

    print(f"Comparing {args.a} ↔ {args.b}")
    print(f"+ added: {len(added)}")
    for k, h, s in list(added)[:10]:
        print("  +", k, h[:8], s)
    if len(added) > 10:
        print(f"  … and {len(added)-10} more")
    print(f"- removed: {len(removed)}")
    for k, h, s in list(removed)[:10]:
        print("  -", k, h[:8], s)


if __name__ == "__main__":
    main()

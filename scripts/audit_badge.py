#!/usr/bin/env python3
"""
Generate a simple status badge for a given audit prefix and upload as status.svg.

Usage:
  python3 scripts/audit_badge.py --prefix audit/2025-08-13
"""
import argparse, datetime as dt, json, os
import boto3

SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="220" height="20">
  <linearGradient id="g" x2="0" y2="100%%"><stop offset="0" stop-opacity=".1" stop-color="#bbb"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <mask id="m"><rect width="220" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="120" height="20" fill="#555"/>
    <rect x="120" width="100" height="20" fill="#2c974b"/>
    <rect width="220" height="20" fill="url(#g)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="60" y="14">xo-audit</text>
    <text x="170" y="14">%s | %s</text>
  </g>
</svg>
"""


def env(n):
    v = os.environ.get(n)
    if not v:
        raise SystemExit(f"missing env {n}")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True)
    args = ap.parse_args()

    ak = env("XO_STORJ_S3_ACCESS_KEY_ID")
    sk = env("XO_STORJ_S3_SECRET_ACCESS_KEY")
    ep = env("XO_STORJ_S3_ENDPOINT")
    bucket = env("XO_STORJ_S3_BUCKET")
    s3 = boto3.client(
        "s3", aws_access_key_id=ak, aws_secret_access_key=sk, endpoint_url=ep
    )

    obj = s3.get_object(Bucket=bucket, Key=f"{args.prefix}/manifest.json")
    man = json.loads(obj["Body"].read().decode())
    count = len(man["objects"])
    day = args.prefix.split("/")[-1]
    svg = SVG % (count, day)
    s3.put_object(
        Bucket=bucket,
        Key=f"{args.prefix}/status.svg",
        Body=svg.encode("utf-8"),
        ContentType="image/svg+xml",
    )
    print(
        f"✅ uploaded status badge to s3://{bucket}/{args.prefix}/status.svg ({count} objects)"
    )


if __name__ == "__main__":
    main()

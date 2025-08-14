#!/usr/bin/env python3
"""
Build a daily Merkle manifest for local artifacts, sign the Merkle root with Vault Transit,
and upload both the artifacts and manifest files to Storj S3 (xo-vault-sealed).

Env (from /tmp/xo-env.sh via Vault Agent or render_xo_env.sh):
  XO_STORJ_S3_ACCESS_KEY_ID
  XO_STORJ_S3_SECRET_ACCESS_KEY
  XO_STORJ_S3_ENDPOINT
  XO_STORJ_S3_BUCKET

Vault env:
  VAULT_ADDR (default: http://127.0.0.1:8200)
  VAULT_TOKEN (if unset, token is read from ~/.config/xo-vault/dev_token)

Usage:
  python3 scripts/audit_build_and_upload.py --src ./artifacts --prefix audit/2025-08-13
"""
import argparse, base64, dataclasses, datetime as dt, hashlib, io, json, os, pathlib, sys, typing
import boto3, requests


def env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if val is None or val == "":
        raise SystemExit(f"❌ required env {name} is missing")
    return val


@dataclasses.dataclass
class ObjMeta:
    key: str
    sha256: str
    size: int


def sha256_file(p: pathlib.Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def merkle_root(hex_hashes: list[str]) -> str:
    if not hex_hashes:
        return hashlib.sha256(b"").hexdigest()
    layer = [bytes.fromhex(h) for h in sorted(hex_hashes)]
    while len(layer) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()


def read_vault_token() -> str:
    tok = os.environ.get("VAULT_TOKEN")
    if tok:
        return tok
    fp = pathlib.Path.home() / ".config/xo-vault/dev_token"
    if not fp.exists():
        raise SystemExit(
            "❌ VAULT_TOKEN not set and dev_token file missing (~/.config/xo-vault/dev_token)"
        )
    return fp.read_text().strip()


def transit_sign(
    vault_addr: str, token: str, key_name: str, merkle_hex_root: str
) -> dict:
    digest_b64 = base64.b64encode(bytes.fromhex(merkle_hex_root)).decode()
    url = f"{vault_addr.rstrip('/')}/v1/transit/sign/{key_name}"
    resp = requests.post(
        url,
        headers={"X-Vault-Token": token},
        json={"hash_algorithm": "sha2-256", "prehashed": True, "input": digest_b64},
        timeout=20,
    )
    if resp.status_code != 200:
        raise SystemExit(f"❌ transit sign failed: {resp.status_code} {resp.text}")
    return resp.json()["data"]  # {signature, key_version, signature_algorithm,...}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--src", required=True, help="Local directory of artifacts to upload"
    )
    ap.add_argument("--prefix", help="S3 prefix (default: audit/YYYY-MM-DD)")
    ap.add_argument(
        "--key", default="xo-audit", help="Vault Transit key name (default: xo-audit)"
    )
    args = ap.parse_args()

    src = pathlib.Path(args.src).resolve()
    if not src.is_dir():
        raise SystemExit(f"❌ src not found: {src}")

    # Env
    ak = env("XO_STORJ_S3_ACCESS_KEY_ID")
    sk = env("XO_STORJ_S3_SECRET_ACCESS_KEY")
    ep = env("XO_STORJ_S3_ENDPOINT")
    bucket = env("XO_STORJ_S3_BUCKET")
    vault_addr = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_token = read_vault_token()

    # Prefix
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")
    prefix = args.prefix or f"audit/{today}"

    # Collect & upload objects (append-only paths)
    s3 = boto3.client(
        "s3", aws_access_key_id=ak, aws_secret_access_key=sk, endpoint_url=ep
    )
    objs: list[ObjMeta] = []

    # Upload each file under {prefix}/objects/{relpath}
    for p in sorted(src.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(src).as_posix()
        key = f"{prefix}/objects/{rel}"
        h, size = sha256_file(p)
        s3.upload_file(str(p), bucket, key)  # no metadata mutations, pure put
        objs.append(ObjMeta(key=key, sha256=h, size=size))

    # Build manifest + merkle
    leaf_hashes = [o.sha256 for o in objs]
    root_hex = merkle_root(leaf_hashes)
    sign_data = transit_sign(vault_addr, vault_token, args.key, root_hex)
    sig = sign_data["signature"]
    key_version = sign_data.get("key_version")

    now_iso = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    manifest = {
        "version": 1,
        "generated_at": now_iso,
        "bucket": bucket,
        "prefix": prefix,
        "transit_key": args.key,
        "key_version": key_version,
        "objects": [dataclasses.asdict(o) for o in objs],
        "merkle_root": root_hex,
        "signature": {
            "type": "vault-transit",
            "algorithm": "ed25519-sha256",
            "key": args.key,
            "key_version": key_version,
            "signature": sig,
            "prehashed": True,
        },
    }

    # Upload manifest files
    manifest_json = json.dumps(manifest, indent=2).encode()
    s3.put_object(Bucket=bucket, Key=f"{prefix}/manifest.json", Body=manifest_json)
    s3.put_object(
        Bucket=bucket, Key=f"{prefix}/manifest.root", Body=(root_hex + "\n").encode()
    )
    s3.put_object(
        Bucket=bucket, Key=f"{prefix}/manifest.root.sig", Body=(sig + "\n").encode()
    )

    print(f"✅ Uploaded {len(objs)} objects and manifest to s3://{bucket}/{prefix}")
    for o in objs[:5]:
        print(f"  - {o.key}  (sha256:{o.sha256[:8]}… size:{o.size})")
    if len(objs) > 5:
        print(f"  … and {len(objs)-5} more")
    print(f"Merkle root: {root_hex}")
    print(f"Transit key: {args.key} v{key_version}, signature: {sig[:16]}…")


if __name__ == "__main__":
    main()

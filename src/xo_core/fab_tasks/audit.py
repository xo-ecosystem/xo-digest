from invoke import task
import os, sys, subprocess, tempfile, pathlib, json, time, random

REPO = pathlib.Path(__file__).resolve().parents[3]


def _py(c, path, args):
    return c.run(f'{sys.executable} "{path}" {args}', pty=True)


def _need_env():
    required = [
        "XO_STORJ_S3_ACCESS_KEY_ID",
        "XO_STORJ_S3_SECRET_ACCESS_KEY",
        "XO_STORJ_S3_ENDPOINT",
        "XO_STORJ_S3_BUCKET",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise SystemExit(
            f"Missing envs {missing}. Run: set -a; source /tmp/xo-env.sh; set +a"
        )


@task
def write_test(c, count=3):
    """
    Generate a few test NDJSON events, build daily manifest (Merkle), sign with Transit, and upload.
    """
    _need_env()
    tmp = pathlib.Path(tempfile.mkdtemp())
    events = []
    for i in range(int(count)):
        p = tmp / f"evt-{int(time.time())}-{random.randrange(1_000_000)}.ndjson"
        p.write_text(json.dumps({"ts": time.time(), "msg": f"hello-{i}"}) + "\n")
        events.append(p.name)
    print(f"Generated {len(events)} events in {tmp}")

    # prefix like audit/YYYY-MM-DD
    from datetime import datetime, timezone

    prefix = f"audit/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    _py(
        c,
        REPO / "scripts/audit_build_and_upload.py",
        f'--src "{tmp}" --prefix "{prefix}"',
    )


@task
def verify(c, prefix):
    """
    Verify manifest signature + Merkle integrity for given S3 prefix.
    """
    _need_env()
    _py(c, REPO / "scripts/audit_verify.py", f'--prefix "{prefix}"')


@task
def diff(c, a, b):
    """Diff two manifests by prefix or local path."""
    _need_env()
    _py(c, REPO / "scripts/audit_diff.py", f'--a "{a}" --b "{b}"')


@task
def badge(c, prefix):
    """Generate and upload status.svg badge for a given audit prefix."""
    _need_env()
    _py(c, REPO / "scripts/audit_badge.py", f'--prefix "{prefix}"')


@task
def rotate_transit(c, key="xo-audit"):
    """Rotate Transit signing key and print new version."""
    os.environ.setdefault("XO_AUDIT_TRANSIT_KEY", key)
    _py(c, REPO / "scripts/audit_rotate_transit.py", "")

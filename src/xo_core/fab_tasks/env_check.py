from invoke import task
import os


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    return value[:4] + "****"


@task
def storj(c):
    keys = [
        "XO_STORJ_S3_ACCESS_KEY_ID",
        "XO_STORJ_S3_SECRET_ACCESS_KEY",
        "XO_STORJ_S3_ENDPOINT",
        "XO_STORJ_S3_BUCKET",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_S3_ENDPOINT",
        "S3_BUCKET",
    ]
    for key in keys:
        value = os.environ.get(key, "")
        if "SECRET" in key or "KEY" in key:
            value = _mask_secret(value)
        print(f"{key}={value}")

from xo_core.metrics import (
    DIGEST_PUBLISHES_TOTAL,
    DIGEST_CONTENT_BYTES_TOTAL,
)


def publish_digest(title: str, content: str, *, fmt: str = "md") -> None:
    # Metrics
    try:
        content_len = len(content.encode("utf-8"))
    except Exception:
        content_len = len(content or "")
    DIGEST_PUBLISHES_TOTAL.labels(format=fmt).inc()
    DIGEST_CONTENT_BYTES_TOTAL.inc(content_len)

    # TODO: implement real publish (files, PR, webhook, etc.)
    print("[digest.publish]", {"title": title, "len": content_len, "format": fmt})

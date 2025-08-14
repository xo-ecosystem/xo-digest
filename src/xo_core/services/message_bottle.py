import asyncio
import json
from typing import Any, Dict, AsyncGenerator, Set, List, Optional
from xo_core.services.bus import get_bus

from xo_core.services.inbox import add_message, append_inbox_message
from xo_core.metrics import (
    MESSAGE_BOTTLE_PUBLISHES_TOTAL,
    MESSAGE_BOTTLE_PAYLOAD_BYTES_TOTAL,
)


_subscribers: Set[asyncio.Queue] = set()
_MB_MESSAGES: List[Dict[str, Any]] = []


class BroadcasterType:
    MEMORY = "memory"
    REDIS = "redis"


async def sse_subscribe() -> AsyncGenerator[str, None]:
    """Async generator yielding SSE chunks for live Message Bottle events."""
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.add(queue)
    try:
        yield f"event: hello\ndata: {json.dumps({'hello': True})}\n\n"
        while True:
            item = await queue.get()
            yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
    finally:
        _subscribers.discard(queue)


def _broadcast(obj: dict) -> None:
    for q in list(_subscribers):
        try:
            q.put_nowait(obj)
        except Exception:
            _subscribers.discard(q)


def publish_message_legacy(data: Dict[str, Any], *, source: str = "api") -> None:
    try:
        payload_len = len(str(data).encode("utf-8"))
    except Exception:
        payload_len = 0
    MESSAGE_BOTTLE_PUBLISHES_TOTAL.labels(source=source).inc()
    MESSAGE_BOTTLE_PAYLOAD_BYTES_TOTAL.inc(payload_len)

    user = str(data.get("user") or data.get("name") or data.get("sender") or "anon")
    msg_text = str(data.get("msg") or data.get("message") or data.get("content") or "")
    entry: Dict[str, Any] | None = None
    if msg_text:
        entry = append_inbox_message("message_bottle", user.strip(), msg_text.strip())

    print("[message_bottle.publish_message]", {"source": source, "len": payload_len})
    add_message(
        {
            "sender": data.get("sender", user),
            "content": data.get("content", msg_text),
            "meta": {"drop": "message_bottle"},
        }
    )

    bus = get_bus()
    asyncio.create_task(
        bus.publish({"type": "message_bottle.new", "payload": entry or data})
    )


async def publish_message(
    drop_id: str | None = None,
    text: str | None = None,
    author: str | None = None,
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Unified publisher supporting ALPHA contract and legacy dict payloads."""
    if data is not None and (drop_id is None and text is None):
        # legacy path
        publish_message_legacy(data, source="api")
        msg = {
            "drop_id": "message_bottle",
            "text": data.get("content") or data.get("message") or "",
            "author": data.get("sender") or data.get("user") or "anon",
        }
    else:
        msg = {
            "drop_id": drop_id or "message_bottle",
            "text": text or "",
            "author": author or "anon",
        }
        publish_message_legacy(
            {"sender": msg["author"], "content": msg["text"]}, source="api"
        )

    _MB_MESSAGES.append(msg)
    _broadcast(msg)
    return msg


async def list_messages(
    limit: int = 20, drop_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    items = [m for m in _MB_MESSAGES if not drop_id or m.get("drop_id") == drop_id]
    return list(reversed(items[-limit:]))


async def subscribe_events_sse(*, request) -> AsyncGenerator[bytes, None]:
    bus = get_bus()
    import json as _json

    async for obj in bus.subscribe():
        if isinstance(obj, dict):
            payload = obj.get("payload", obj)
            try:
                yield _json.dumps(payload, ensure_ascii=False).encode("utf-8")
            except Exception:
                continue

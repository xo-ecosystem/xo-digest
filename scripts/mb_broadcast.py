#!/usr/bin/env python3
"""
CLI to publish Message Bottle events into the SSE bus.
Works with in-memory bus (no REDIS_URL) or Redis pub/sub (set REDIS_URL).

Examples:
  python scripts/mb_broadcast.py --name test --message "hello!"
  REDIS_URL=redis://localhost:6379/0 python scripts/mb_broadcast.py -n XO -m "wave"
  python scripts/mb_broadcast.py -n XO -m "storm" --count 5 --interval 1.0
"""
import os
import sys
import json
import asyncio
import argparse
from datetime import datetime, timezone

# allow "python scripts/mb_broadcast.py" to import project code
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from xo_core.services.bus import get_bus  # type: ignore


def build_event(name: str, message: str, extra: dict | None = None) -> dict:
    payload = {
        "name": name,
        "message": message,
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "cli",
    }
    if extra:
        payload.update(extra)
    return {"type": "message_bottle.new", "payload": payload}


async def main():
    p = argparse.ArgumentParser(
        description="Broadcast a Message Bottle event to SSE bus"
    )
    p.add_argument("-n", "--name", default="CLI", help="Sender name")
    p.add_argument("-m", "--message", required=True, help="Message text")
    p.add_argument(
        "--json", help="Optional JSON to merge into payload (string or @file.json)"
    )
    p.add_argument("--count", type=int, default=1, help="How many events to send")
    p.add_argument("--interval", type=float, default=0.0, help="Seconds between events")
    args = p.parse_args()

    extra = None
    if args.json:
        src = args.json
        if src.startswith("@"):
            with open(src[1:], "r", encoding="utf-8") as f:
                extra = json.load(f)
        else:
            extra = json.loads(src)

    bus = get_bus()
    for i in range(args.count):
        evt = build_event(args.name, args.message, extra)
        await bus.publish(evt)
        print(f"[broadcasted] {evt}")
        if i + 1 < args.count and args.interval > 0:
            await asyncio.sleep(args.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

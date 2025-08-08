#!/usr/bin/env python3
"""Minimal VRChat OSC mock to toggle a glow parameter based on traits.

Usage:
  python scripts/vrchat_osc_mock.py --drop message_bottle --param GlowOn

This sends an OSC boolean to localhost:9000 (VRChat default). For demo only.
"""

from __future__ import annotations

import argparse
import socket
from typing import Tuple

from src.xo_core.utils.traits import load_traits


def send_osc_bool(
    address: str, value: bool, host: str = "127.0.0.1", port: int = 9000
) -> None:
    # Extremely small OSC encoder for /address, i, value
    def pad(s: bytes) -> bytes:
        return s + (b"\x00" * ((4 - (len(s) % 4)) % 4))

    typetags = b",i"
    message = (
        pad(address.encode("utf-8") + b"\x00")
        + pad(typetags + b"\x00")
        + (value and (1).to_bytes(4, "big") or (0).to_bytes(4, "big"))
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (host, port))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--drop", required=True, help="Drop ID (directory under drops/)"
    )
    parser.add_argument(
        "--param", default="GlowOn", help="VRChat avatar parameter name"
    )
    args = parser.parse_args()

    traits = load_traits(args.drop)
    enable = any(
        bool(t.get("game_effects", {}).get("vrchat", {}).get("glow_on")) for t in traits
    )
    address = f"/avatar/parameters/{args.param}"
    send_osc_bool(address, enable)
    print(f"Sent {enable} to {address}")


if __name__ == "__main__":
    main()

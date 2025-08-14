import asyncio
import os
import json

from redis import asyncio as redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL = os.getenv("XO_COLOR_WAVE_CHANNEL", "color_wave_updates")


async def main() -> None:
    client = redis.from_url(REDIS_URL, decode_responses=True)
    test_wave = {
        "fade_speed": 0.8,
        "trail_length": 8,
        "colors": ["#FFD700", "#FF69B4", "#1E90FF"],
    }
    try:
        await client.publish(CHANNEL, json.dumps(test_wave))
        print(f"Published test wave to {CHANNEL}: {test_wave}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

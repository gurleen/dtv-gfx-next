import asyncio
import random


async def producer(q: asyncio.Queue):
    while True:
        await q.put(("homeScore", random.randint(0, 49)))
        await asyncio.sleep(2)


async def producer_two(q: asyncio.Queue):
    while True:
        await q.put(("awayScore", random.randint(50, 99)))
        await asyncio.sleep(0.5)

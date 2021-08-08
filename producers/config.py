import aiofiles
import asyncio


async def read_from_config(q: asyncio.Queue):
    async with aiofiles.open("CONFIG", mode="r") as f:
        async for line in f:
            key, value = line.split("=")
            print(key, value.strip())
            await q.put((key, value))
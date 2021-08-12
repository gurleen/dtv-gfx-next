import aiofiles
import asyncio
from loguru import logger


async def read_from_config(q: asyncio.Queue):
    logger.info("Loading CONFIG file...")
    async with aiofiles.open("CONFIG", mode="r") as f:
        async for line in f:
            key, value = line.split("=")
            await q.put((key, value))
from kv_queue import KeyValueQueue
import aiofiles
from loguru import logger


async def read_from_config(q: KeyValueQueue):
    logger.info("Loading CONFIG file...")
    async with aiofiles.open("CONFIG", mode="r") as f:
        async for line in f:
            key, value = line.split("=")
            await q.data(key, value.strip())
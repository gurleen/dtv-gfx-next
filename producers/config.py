import os
import sys
from pathlib import Path
from kv_queue import KeyValueQueue
import aiofiles
from loguru import logger


if getattr("sys", "frozen", False):
    app_path = sys._MEIPASS
else:
    app_path = Path(os.path.dirname(os.path.abspath(__file__))).parent


async def read_from_config(q: KeyValueQueue):
    logger.info("Loading CONFIG file...")
    async with aiofiles.open(os.path.join(app_path, "CONFIG"), mode="r") as f:
        async for line in f:
            key, value = line.split("=")
            await q.data(key, value.strip())
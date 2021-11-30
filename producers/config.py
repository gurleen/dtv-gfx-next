import os
import sys
from pathlib import Path
from janus import Queue
import aiofiles
from loguru import logger

from .decorator import producer


if getattr("sys", "frozen", False):
    app_path = sys._MEIPASS
else:
    app_path = Path(os.path.dirname(os.path.abspath(__file__))).parent


@producer
async def read_from_config(q: Queue):
    logger.info("Loading CONFIG file...")
    async with aiofiles.open(os.path.join(app_path, "CONFIG"), mode="r") as f:
        async for line in f:
            key, value = line.split("=")
            await q.async_q.put({key: value.strip()})

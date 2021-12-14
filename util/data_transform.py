from typing import Mapping
from loguru import logger
from janus import Queue
from first import first
from operator import itemgetter as get

from .store import store


async def process_control_data(queue: Queue):
    while True:
        message: Mapping = await queue.async_q.get()
        print(store)
        logger.debug(message)
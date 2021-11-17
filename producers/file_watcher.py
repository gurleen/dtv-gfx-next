from kv_queue import KeyValueQueue
import time
import asyncio
from watchgod import awatch


FILE_NAME = "/srv/ftp/test"


async def watch_file(q: KeyValueQueue):
    loop = asyncio.get_event_loop()
    async for changes in awatch("/srv/ftp/test"):
        print(changes)
        result = await loop.run_in_executor(None, process_file)
        print(result)


def process_file():
    time.sleep(5)
    return "hello!"

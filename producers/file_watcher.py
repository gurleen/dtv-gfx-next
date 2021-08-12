import time
import asyncio
import concurrent.futures
import aiofiles
from watchgod import awatch


FILE_NAME = "/srv/ftp/test"


async def watch_file(q: asyncio.Queue):
    loop = asyncio.get_event_loop()
    async for changes in awatch("/srv/ftp/test"):
        print(changes)
        result = await loop.run_in_executor(None, process_file)
        print(result)


def process_file():
    time.sleep(5)
    return "hello!"
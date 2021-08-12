import asyncio
import aiofiles
from watchgod import awatch


async def watch_file(q: asyncio.Queue):
    async for changes in awatch("/srv/ftp/test"):
        print(changes)
        async with aiofiles.open("/srv/ftp/test", mode="r") as f:
            async for line in f:
                print(line)
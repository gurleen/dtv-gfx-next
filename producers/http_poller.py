import asyncio
import aiohttp
from loguru import logger
from janus import Queue

from producers.parse_xml import parse
from producers.decorator import producer
from util.store import store

URL = "http://192.155.88.183:8000/11.xml"


async def poll_stats(q: Queue):
    logger.info(f"Pulling StatCrew XML from {URL}.")
    loop = asyncio.get_event_loop()
    cache = None
    data_cache = None
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(URL) as resp:
                raw_xml = await resp.text()
                if raw_xml != cache:
                    data = await loop.run_in_executor(None, parse, raw_xml)
                    if data != data_cache:
                        await q.async_q.put({"stats": data})
                        store["stats"] = data
                        data_cache = data
                    cache = raw_xml
            await asyncio.sleep(1)

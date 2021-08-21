import asyncio
from collections import defaultdict
from typing import Dict

from aiohttp import web
import socketio
from loguru import logger

from producers.file_watcher import watch_file
from producers.serial import read_allsport_cg
from producers.config import read_from_config
from kv_queue import KeyValueQueue


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
q = KeyValueQueue()

app.router.add_static("/", "static", show_index=True)


cache = defaultdict(dict)


async def consumer(q: KeyValueQueue):
    while True:
        key, value, msg_type = await q.get()
        cache[msg_type][key] = value
        await sio.emit(msg_type, {key: value})


@sio.on("get-data-cache")
async def get_cache(sid):
    await sio.emit("data-update", cache["data-update"])


@sio.on("set-key")
async def set_key(sid, data: Dict):
    await q.put((data["key"], data["value"], data["type"]))


@sio.event
def connect(sid, environ, _):
    ip = environ.get("REMOTE_ADDR")
    logger.info(f"Client at {ip} with sid {sid} connected.")


def main():
    loop = asyncio.get_event_loop()

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner)
    loop.run_until_complete(site.start())

    loop.create_task(consumer(q))
    loop.create_task(read_from_config(q))
    loop.create_task(read_allsport_cg(q, loop))
    loop.create_task(watch_file(q))

    try:
        print("Welcome to dtv-gfx-next 🐉")
        print("Go Dragons!\n")
        logger.info("Running graphics server...")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Goodbye!")
        quit()


main()

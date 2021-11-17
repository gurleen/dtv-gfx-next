import os
import sys
import json
import asyncio
import socketio
from janus import Queue
from loguru import logger
from aiohttp import web
from distutils.util import strtobool

import producers
from producers.http_poller import poll_stats
from util.colors import colorscale
from util.config_menu import config_window
import global_vars


cache = dict()
queue = None


DEBUG = strtobool(os.getenv("DEBUG", default="false"))
if getattr("sys", "frozen", False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))


logger.remove()
log_level = "DEBUG" if DEBUG else "INFO"
logger.add(sys.stderr, level=log_level)


async def generate_styles(request):
    colors = {k: v for k, v in cache.items() if "color" in k.lower()}
    rv = ""
    for k, c in colors.items():
        rv += f".{k} {{ background-color: {c}; }}\n"
        rv += f".{k}Darker {{ background-color: {colorscale(c, 0.6)}; }}\n"
    return web.Response(text=rv, content_type="text/css")


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
app.add_routes([web.get("/styles", generate_styles)])
app.router.add_static("/", os.path.join(app_path, "static"), show_index=True)


async def consumer(queue: Queue):
    while True:
        message: dict = await queue.async_q.get()
        cache.update(message)
        await sio.emit("state-update", message)


@sio.on("get-cache")
def get_cache(sio):
    return cache


@sio.on("get-key")
def get_key(sio, key):
    return cache.get(key)


@sio.on("update-key")
async def update_key(sio, key, value):
    logger.debug(f"{key}: {value}")
    await queue.async_q.put({key: value})


@sio.event
def connect(sid, environ, _):
    ip = environ.get("REMOTE_ADDR")
    logger.info(f"Client at {ip} with sid {sid} connected.")


async def create_queue(defaults: dict) -> Queue:
    q = Queue()
    await q.async_q.put(defaults)
    return q


def setup_services(loop):
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner)
    loop.run_until_complete(site.start())
    

async def rerun_on_exception(coro, *args, **kwargs):
    while True:
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            # don't interfere with cancellations
            raise
        except Exception:
            print("Caught exception")


def main():
    global queue
    data = dict()

    if not DEBUG:
        data = config_window()
        global_vars.COM_PORT = data["com_port"]

    logger.info("Welcome to dtv-gfx-next 🐉")
    logger.info("Go Dragons!")
    if DEBUG:
        logger.info("RUNNING IN DEBUG MODE.")

    loop = asyncio.get_event_loop()
    print("DATA:", data)
    queue = loop.run_until_complete(create_queue(data))
    prods = producers.collect_producers()
    setup_services(loop)

    loop.create_task(consumer(queue))
    loop.create_task(rerun_on_exception(poll_stats, queue))

    logger.info("Initializing producers...")

    for producer, debug_only, prod_only in prods:
        should_run = any(
            (
                (DEBUG and debug_only),
                (not DEBUG and prod_only),
                (not debug_only and not prod_only),
            )
        )

        if should_run:
            loop.create_task(producer(queue))

    logger.info("All producers initialized.")

    logger.info("Starting async event loop")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("", end="\r")
        logger.info("Shutting down...")
        loop.stop()
        quit()


if __name__ == "__main__":
    main()

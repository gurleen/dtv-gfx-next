import os
import sys
import json
import asyncio
import socketio
from janus import Queue
from loguru import logger
from aiohttp import web
from amcp_pylib.core import Client
from amcp_pylib.module.basic import LOADBG, PLAY, CLEAR
from amcp_pylib.module.template import CG_ADD
from distutils.util import strtobool

import producers
from producers.http_poller import poll_stats
from producers.livestats import listen_to_nls
from util.colors import colorscale
from util.config_menu import config_window
from util.data_transform import process_control_data
import global_vars


cache = dict()
queue: Queue = None
control_queue: Queue = None


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


async def get_full_cache(request):
    return web.Response(text=json.dumps(cache), content_type="application/json")


caspar = Client()
caspar.connect()
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)
app.add_routes([web.get("/styles", generate_styles), web.get("/cache", get_full_cache)])
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
    print(key, value)
    await queue.async_q.put({key: value})


@sio.on("control-message")
async def control_message(sio, key, value):
    """Handle message from control panel."""
    await control_queue.async_q.put({key: value})


@sio.on("casparcg")
async def casparcg(sio, action, item, layer):
    """Handle CasparCG event."""
    print("CASPARCG", action, item, layer)
    if action == "LOAD AND PLAY":
        caspar.send(LOADBG(channel=1, layer=layer, clip=item))
        caspar.send(PLAY(video_channel=1, layer=layer, clip=item))
        caspar.send(LOADBG(channel=1, layer=layer, clip="EMPTY", transition="MIX", duration= 20, auto="AUTO"))
    elif action == "QUEUE":
        caspar.send(LOADBG(channel=1, layer=layer, clip=item, auto="AUTO"))
    elif action == "QUEUE BLANK":
        caspar.send(LOADBG(channel=1, layer=layer, clip="EMPTY", transition="MIX", duration= 1, auto="AUTO"))
    elif action == "CG ADD":
        caspar.send(CG_ADD(video_channel=1, cg_layer=layer, template=item, play_on_load=1))
    elif action == "BLANK":
        caspar.send(CLEAR(video_channel=1))
    elif action == "CLEAR":
        caspar.send(CLEAR(video_channel=1, layer=layer))

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
    global queue, control_queue
    data = dict()

    if not DEBUG:
        data = config_window()
        global_vars.COM_PORT = data["com_port"]

    logger.info("Welcome to dtv-gfx-next 🐉")
    logger.info("Go Dragons!")
    if DEBUG:
        logger.info("RUNNING IN DEBUG MODE")

    loop = asyncio.get_event_loop()
    queue = loop.run_until_complete(create_queue(data))
    control_queue = loop.run_until_complete(create_queue(data))
    prods = producers.collect_producers()
    setup_services(loop)

    loop.create_task(consumer(queue))
    loop.create_task(rerun_on_exception(poll_stats, queue))
    # loop.create_task(listen_to_nls(queue))
    loop.create_task(process_control_data(control_queue))

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

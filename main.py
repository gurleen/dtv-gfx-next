import os
import asyncio
from asyncio import Queue

from aiohttp import web
import socketio

from producers.randint import producer, producer_two


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

app.router.add_static("/", "static", show_index=True)


cache = dict()

async def consumer(q: Queue):
    while True:
        key, value = await q.get()
        cache[key] = value
        await sio.emit("data-update", {key: value})

@sio.on("get-cache")
async def get_cache(sid):
    await sio.emit("data-update", cache)


@sio.event
def connect(sid, environ, _):
    ip = environ.get("REMOTE_ADDR")
    print(f"Client at {ip} with sid {sid} connected.")


def main():
    q = Queue()
    loop = asyncio.get_event_loop()

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner)
    loop.run_until_complete(site.start())

    loop.create_task(producer(q))
    loop.create_task(producer_two(q))
    loop.create_task(consumer(q))

    try:
        print("Running graphics server...")
        loop.run_forever()
    except KeyboardInterrupt:
        print("Goodbye!")
        quit()

main()
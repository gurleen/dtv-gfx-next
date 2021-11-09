import os
import sys
import time
import asyncio
from collections import defaultdict
from typing import Dict

from aiohttp import web
import socketio
from loguru import logger
import PySimpleGUI as sg
from serial.tools.list_ports import comports

from producers.file_watcher import watch_file
from producers.serial import read_allsport_cg, mock_allsport_cg
from producers.config import read_from_config
from kv_queue import KeyValueQueue
from util.ident_fetch import get_items, get_ident, CONF_ROOT
from producers.http_poller import poll_stats


if getattr("sys", "frozen", False):
    app_path = sys._MEIPASS
else:
    app_path = os.path.dirname(os.path.abspath(__file__))


sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
q: KeyValueQueue

app.router.add_static("/", os.path.join(app_path, "static"), show_index=True)


cache = defaultdict(dict)


async def consumer(q: KeyValueQueue):
    while True:
        key, value, msg_type = await q.get()
        cache[msg_type][key] = value
        await sio.emit(msg_type, {key: value})


@sio.on("get-data-cache")
async def get_cache(sid):
    await sio.emit("data-update", cache["data-update"])


@sio.on("get-key")
def get_key(sid, key: str):
    return cache["data-update"][key]


@sio.on("set-key")
async def set_key(sid, data: Dict):
    await q.put((data["key"], data["value"], data["type"]))


@sio.event
def connect(sid, environ, _):
    ip = environ.get("REMOTE_ADDR")
    logger.info(f"Client at {ip} with sid {sid} connected.")


def config_window():
    ports = comports()
    confs = get_items(CONF_ROOT)
    teams = []
    layout = [
        [sg.Text("DragonsTV Graphics Config")],
        [sg.Text("Set Away Team")],
        [sg.Combo([x[0] for x in confs], enable_events=True)],
        [sg.Combo([], enable_events=True, key="-TEAMS-", expand_x=True)],
        [sg.Text("Select AllSport CG Port")],
        [sg.Combo(ports, key="-SERIAL-")],
        [sg.Button("OK")]
    ]
    window = sg.Window("DragonsTV Graphics", layout)
    while True:
        event, values = window.read()
        if event == "OK" and values[0] and values["-TEAMS-"]:
            team_obj = next((x for x in teams if x[0] == values["-TEAMS-"]))
            ident = get_ident(team_obj[1])
            window.close()
            return (*ident, values["-SERIAL-"])
        elif event == sg.WINDOW_CLOSED:
            window.close()
            quit()
        elif event == 0:
            conf_obj = next((x for x in confs if x[0] == values[0]))
            teams = get_items(conf_obj[1])
            window["-TEAMS-"].update(values=[x[0] for x in teams])


async def create_queue():
    global q
    q = KeyValueQueue()


def main():
    global q
    serial = None
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_queue())

    if "--skip-team" not in sys.argv:
        away_color, away_image, serial = config_window()
        loop.run_until_complete(q.data("awayColor", away_color))
        loop.run_until_complete(q.data("awayImage", away_image))

    print("Serial:", serial)

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner)
    loop.run_until_complete(site.start())

    loop.create_task(consumer(q))
    loop.create_task(read_from_config(q))
    loop.create_task(poll_stats(q))

    if serial:
        loop.create_task(read_allsport_cg(q, loop, serial.device))
    else:
        loop.create_task(mock_allsport_cg(q))
    # loop.create_task(watch_file(q))

    try:
        print("Welcome to dtv-gfx-next 🐉")
        print("Go Dragons!\n")
        logger.info("Running graphics server...")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Goodbye!")
        quit()


main()

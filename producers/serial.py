import asyncio
from janus import Queue
import random
import itertools
from typing import Optional

import serial_asyncio
from loguru import logger
from producers.decorator import producer
from global_vars import COM_PORT


class Output(asyncio.Protocol):
    line = b""
    cache = {}

    def __init__(self, q: Queue) -> None:
        super().__init__()
        self.queue = q

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
        transport.serial.rts = False
        logger.info("Connected to AllSport CG.")

    def data_received(self, data) -> None:
        if b'\x04' in data:
            asyncio.ensure_future(self.flush_data(), loop=asyncio.get_event_loop())
        else:
            self.line += data

    async def flush_data(self) -> None:
        line = self.line.decode("ascii").lstrip("\x01")
        rv = {
            "clock": line[0:5].strip(),
            "shotClock": line[8:11].strip(),
            "homeScore": line[13:15].strip(),
            # "homeScore": line[25:27].strip(),
            # "awayScore": line[27:29].strip()
            "awayScore": line[16:18].strip()
        }
        for k, v in rv.items():
            self.cache[k] = v
        await self.queue.async_q.put(rv)
        self.line = b""

    def connection_lost(self, exc: Optional[Exception]) -> None:
        logger.error("Connection to serial port lost!")

@producer(prod_only=True)
def read_allsport_cg(q: Queue, port: str = COM_PORT):
    loop = asyncio.get_event_loop()
    print(port)
    if port:
        return serial_asyncio.create_serial_connection(
            loop, lambda: Output(q), port
        )
    else:
        logger.info("COM Port not provided - defaulting to mock AllSport")
        return mock_allsport_cg(q)

@producer(debug_only=True)
async def mock_allsport_cg(q: Queue):
    logger.info("Running MOCK AllSport CG.")
    periods = itertools.cycle(("1st", "2nd", "3rd", "4th"))
    home, away = 0, 0
    duration = 10
    shot_clock = 30
    while True:
        duration -= 1
        shot_clock -= 1
        if duration <= 0: 
            duration = 10
            await q.async_q.put({"period": next(periods)})
        if shot_clock <= 0: shot_clock = 30
        min, sec = duration // 60, duration % 60
        time = f"{min}:{sec:02}"
        x = random.random()
        if x < 0.1:
            home += 2
        elif x < 0.2:
            away += 2
        payload = dict(
            homeScore=home,
            awayScore=away,
            clock=time,
            shotClock=shot_clock
        )
        await q.async_q.put(payload)
        await asyncio.sleep(1)

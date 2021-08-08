import asyncio
import random
import itertools
from typing import Optional

import serial_asyncio


class Output(asyncio.Protocol):
    def __init__(self, q: asyncio.Queue) -> None:
        super().__init__()
        self.queue = q

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
        transport.serial.rts = False

    async def data_received(self, data: bytes) -> None:
        await q.put(repr(bytes))

    def connection_lost(self, exc: Optional[Exception]) -> None:
        print("Connection to serialport lost!")


def read_allsport_cg(q: asyncio.Queue, loop: asyncio.AbstractEventLoop):
    return serial_asyncio.create_serial_connection(
        loop, lambda: Output(q), "/dev/ttyUSB0", baudrate=115200
    )


async def mock_allsport_cg(q: asyncio.Queue):
    periods = itertools.cycle(("1st", "2nd", "3rd", "4th"))
    home, away = 0, 0
    duration = 10
    shot_clock = 30
    while True:
        duration -= 1
        shot_clock -= 1
        if duration <= 0: 
            duration = 10
            await q.put(("period", next(periods)))
        if shot_clock <= 0: shot_clock = 30
        min, sec = duration // 60, duration % 60
        time = f"{min}:{sec:02}"
        await q.put(("clock", time))
        await q.put(("shotClock", shot_clock))
        x = random.random()
        if x < 0.1:
            home += 2
            await q.put(("homeScore", home))
        elif x < 0.2:
            away += 2
            await q.put(("awayScore", away))
        await asyncio.sleep(1)
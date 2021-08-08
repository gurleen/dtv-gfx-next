import asyncio
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

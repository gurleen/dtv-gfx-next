import asyncio
from enum import Enum
from janus import Queue
from typing import Union
from dataclasses import dataclass


@dataclass
class QueueItem:
    key: str
    value: Union[str, int, float, list, dict]


class CustomQueue:
    q: Queue

    def __init__(self):
        self.q = Queue()

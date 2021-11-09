from janus import Queue
from typing import Any, Coroutine


class KeyValueQueue:
    queue: Queue

    def __init__(self):
        self.queue = Queue()

    async def data(self, key: str, value: str):
        return await self.queue.async_q.put((key, value, "data-update"))

    async def state(self, key: str, value: str):
        return await self.queue.async_q.put((key, value, "state-update"))

    async def obj(self, key: str, value: Any):
        return await self.queue.async_q.put((key, value, "object-update"))

    async def put(self, item: Any):
        await self.queue.async_q.put(item)

    async def get(self):
        return await self.queue.async_q.get()

    def sync_put(self, item: Any):
        self.queue.sync_q.put(item)
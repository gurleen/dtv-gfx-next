from asyncio import Queue
from typing import Any, Coroutine


class KeyValueQueue(Queue):
    def data(self, key: str, value: str) -> Coroutine[Any, Any, None]:
        return self.put((key, value, "data-update"))

    def state(self, key: str, value: str) -> Coroutine[Any, Any, None]:
        return self.put((key, value, "state-update"))
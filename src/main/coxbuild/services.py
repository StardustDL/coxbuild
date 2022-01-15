import asyncio
from cgitb import handler
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Tuple

from .runners import Runner


@dataclass
class EventHandler:
    event: Callable[[], Awaitable]
    handler: Callable[[], None]
    repeat: int = 0

    async def handle(self):
        while True:
            await self.event()
            self.handler()

            if self.repeat == 0:
                break
            elif self.repeat > 0:
                self.repeat -= 1


class Service:
    def __init__(self) -> None:
        self.handlers: list[EventHandler] = []

    def register(self, handler: EventHandler):
        self.handlers.append(handler)

    async def _run(self):
        await asyncio.gather(*[e.handle() for e in self.handlers])

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        asyncio.run(self._run())

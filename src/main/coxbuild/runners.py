import asyncio
from datetime import timedelta
import inspect
from timeit import default_timer as timer
from typing import Awaitable, Callable


class Runner:
    """Generic async runner."""

    def __init__(self, func: Callable[[], Awaitable | None]) -> None:
        self.func = func
        self.duration = timedelta()
        self.exc_type = None
        self.exc_value = None
        self.exc_tb = None

    async def __aenter__(self) -> Callable[[], Awaitable | None]:
        self._tic = timer()

        return self.func

    async def __aexit__(self, exc_type, exc_value, exc_tb) -> bool:
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_tb = exc_tb

        self.duration = timedelta(seconds=timer()-self._tic)

        del self._tic
        return True

    def __await__(self):
        async def wrapper():
            async with self as run:
                res = run()
                if inspect.isawaitable(res):
                    res = await res
        yield from wrapper().__await__()
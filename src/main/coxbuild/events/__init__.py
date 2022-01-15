import asyncio
import functools
from datetime import date, datetime, time, timedelta
from typing import Awaitable, Callable, ParamSpec

P = ParamSpec("P")


def event(f: Callable[P, Awaitable]) -> Callable[P, Callable[[], Awaitable]]:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        async def inner():
            awaitable = f(*args, **kwargs)
            await awaitable
        return inner

    return wrapper


@event
async def delay(duration: timedelta):
    await asyncio.sleep(duration.total_seconds())

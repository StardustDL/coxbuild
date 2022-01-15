import asyncio
import functools
from datetime import date, datetime, time, timedelta
from typing import Awaitable, Callable, ParamSpec

from ..exceptions import EventCannotOccur

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


@event
async def atdate(day: date):
    now = datetime.now()
    if now.date() == day:
        return
    elif now.date() < day:
        await delay(datetime(day.year, day.month, day.day)-now)()
    else:
        raise EventCannotOccur()


@event
async def atdatetime(dt: datetime):
    now = datetime.now()
    ntm = now.time()
    if now.date() == dt.date() and ntm.hour == dt.hour and ntm.minute == dt.minute and ntm.second == dt.second:
        return
    elif now < dt:
        await delay(dt - now)()
    else:
        raise EventCannotOccur()


@event
async def attime(offset: time):
    now = datetime.now()
    ntm = now.time()
    if ntm.hour == offset.hour and ntm.minute == offset.minute and ntm.second == offset.second:
        return
    elif now.time() < offset:
        await delay(datetime(now.year, now.month, now.day, offset.hour, offset.minute, offset.second)-now)()
    else:
        await delay(datetime(now.year, now.month, now.day, offset.hour, offset.minute, offset.second)+timedelta(days=1)-now)()

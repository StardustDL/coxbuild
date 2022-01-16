import asyncio
import functools
import logging
from datetime import date, datetime, time, timedelta
from typing import AsyncIterator, Awaitable, Callable, ParamSpec

from ..services import EventContext, EventType

P = ParamSpec("P")

logger = logging.getLogger("events")


def onceevent(f: Callable[P, Awaitable[EventContext | None]]) -> Callable[P, EventType]:
    """Wrap an awaitable function into event function."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        async def inner():
            awaitable = f(*args, **kwargs)
            result = await awaitable
            yield result
        return inner()

    return wrapper


@onceevent
async def delay(duration: timedelta):
    await asyncio.sleep(duration.total_seconds())


async def repeat(eventBuilder: Callable[[], EventType], repeat: int = 0, continueOnError: bool = False):
    """
    Repeat event.

    eventBuilder: a callable that return event
    repeat: repeat times, 0 for no-repeat, positive integer for finite repeat, negative integer for infinite repeat
    continueOnError: continue repeat when error
    """

    if repeat >= 0:
        repeat += 1

    cnt = 0

    while repeat != 0:
        cnt += 1
        logger.debug(f"repeat the {cnt} time.")
        try:
            async for context in eventBuilder():
                yield context
        except Exception as ex:
            logger.error(f"Error when repeat the {cnt} time.", exc_info=ex)
            if continueOnError:
                logger.info(f"Continue repeat on error.")
            else:
                raise
        finally:
            if repeat > 0:
                repeat -= 1


def forever(eventBuilder: Callable[[], EventType]):
    """Repeat forever"""
    return repeat(eventBuilder, -1)


def periodic(period: timedelta):
    """Occur forever in an interval."""
    return forever(lambda: delay(period))


async def limit(event: EventType, number: int = 1):
    """
    Limit event occur times.

    number: limit times, 0 for no-occur, positive integer for finite occur, negative integer for infinite occur
    """
    if number == 0:
        return

    async for context in event:
        yield context

        if number > 0:
            number -= 1

        if number == 0:
            break


def once(event: EventType):
    """
    Occur event once.
    """
    return limit(event, 1)


async def occur(event: EventType):
    """
    Create an awaitable for occuring event once.
    """
    async for context in event:
        return context

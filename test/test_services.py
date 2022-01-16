import asyncio
from datetime import timedelta
from coxbuild.services import EventHandler, Service
from coxbuild.events import delay, onceevent
import pytest


@pytest.mark.asyncio
async def test_service():
    ser = Service()
    c = 0

    def handler():
        nonlocal c
        c = 1

    eh = EventHandler(delay(timedelta(seconds=0.2)), handler)
    ser.register(eh)
    await ser()

    assert c == 1


@pytest.mark.asyncio
async def test_asynchandler():
    ser = Service()
    c = 0

    async def handler():
        nonlocal c
        await asyncio.sleep(0.2)
        c = 1

    eh = EventHandler(delay(timedelta(seconds=0.2)), handler)
    ser.register(eh)
    await ser()

    assert c == 1


@pytest.mark.asyncio
async def test_unsafehandler():
    ser = Service()
    c = 0

    def handler():
        nonlocal c
        raise Exception("unsafe")
        c = 1

    eh = EventHandler(delay(timedelta(seconds=0.2)), handler, safe=True)
    ser.register(eh)
    await ser()

    assert c == 0


@pytest.mark.asyncio
async def test_unsafeevent():
    ser = Service()
    c = 0

    @onceevent
    async def event():
        raise Exception("unsafe")

    eh = EventHandler(event(), lambda: None, safe=True)
    ser.register(eh)
    await ser()

    assert c == 0

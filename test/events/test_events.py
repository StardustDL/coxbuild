from datetime import timedelta
from coxbuild.events import delay, limit, occur, once, periodic
import pytest


@pytest.mark.asyncio
async def test_delay():
    c = 0
    async for _ in delay(timedelta(seconds=0.2)):
        c = 1
    assert c == 1


@pytest.mark.asyncio
async def test_periodic():
    c = 0
    async for _ in periodic(timedelta(seconds=0.1)):
        c += 1
        if c >= 5:
            break
    assert c == 5


@pytest.mark.asyncio
async def test_limit():
    c = 0
    async for _ in limit(periodic(timedelta(seconds=0.1)), 3):
        c += 1
    assert c == 3


@pytest.mark.asyncio
async def test_once():
    c = 0
    async for _ in once(periodic(timedelta(seconds=0.1))):
        c += 1
    assert c == 1


@pytest.mark.asyncio
async def test_occur():
    c = 0
    await occur(periodic(timedelta(seconds=0.1)))
    assert c == 0

import asyncio
from coxbuild.runners import Runner

import pytest


@pytest.mark.asyncio
async def test_normal():
    c = 0

    def f():
        nonlocal c
        c = 1

    r = Runner(f)
    await r
    assert c == 1
    assert not r.exc_value


@pytest.mark.asyncio
async def test_async():
    c = 0

    async def f():
        nonlocal c
        await asyncio.sleep(0.1)
        c = 1

    r = Runner(f)
    await r
    assert c == 1
    assert not r.exc_value


@pytest.mark.asyncio
async def test_fail():
    c = 0

    async def f():
        nonlocal c
        raise Exception("exception")
        c = 1

    r = Runner(f)
    await r
    assert c == 0
    assert r.exc_value

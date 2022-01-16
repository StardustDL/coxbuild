import asyncio
from coxbuild.tasks import Task

import pytest


@pytest.mark.asyncio
async def test_normal():
    c = 0

    def f():
        nonlocal c
        c = 1

    r = Task(body=f)
    res = await r()
    assert res
    assert c == 1


@pytest.mark.asyncio
async def test_async():
    c = 0

    async def f():
        nonlocal c
        await asyncio.sleep(0.1)
        c = 1

    r = Task(body=f)
    res = await r()
    assert res
    assert c == 1


@pytest.mark.asyncio
async def test_fail():
    c = 0

    async def f():
        nonlocal c
        raise Exception("exception")
        c = 1

    r = Task(body=f)
    res = await r()
    assert not res
    assert c == 0


@pytest.mark.asyncio
async def test_precond_ignore():
    c = 0

    def add():
        nonlocal c

    r = Task(body=add, precondition=lambda: False)
    res = await r(setup=add, teardown=add)
    assert res
    assert c == 0


@pytest.mark.asyncio
async def test_postcond_fail():
    c = 0

    def f():
        nonlocal c
        c = 1

    r = Task(body=f, postcondition=lambda: c == 0)
    res = await r()
    assert not res
    assert c == 1


@pytest.mark.asyncio
async def test_hook():
    c = 0

    def add():
        nonlocal c
        c += 1

    r = Task(body=add)
    res = await r(setup=add, teardown=add)
    assert res
    assert c == 3

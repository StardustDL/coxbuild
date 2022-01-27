import asyncio

import pytest

from coxbuild.pipelines import Pipeline, PipelineBeforeTaskHook, PipelineHook, TaskHook
from coxbuild.tasks import Task


def taskpre(l: list):
    def f():
        l.append(0)

    return Task("pre", f)


def task1(l: list):
    def f():
        l.append(1)

    return Task("1", f, deps=["pre"])


def pipe(data: list) -> Pipeline:
    p = Pipeline()
    p.register(task1(data))
    p.register(taskpre(data))
    return p


@pytest.mark.asyncio
async def test_normal():
    data = []
    p = pipe(data)
    res = await p("1")
    assert res
    assert len(data) == 2
    assert data[0] == 0
    assert data[1] == 1


@pytest.mark.asyncio
async def test_pipeline_before_ignore():
    data = []
    p = pipe(data)
    p.beforeTask(lambda a: False)

    res = await p("1")
    assert res
    assert len(data) == 0

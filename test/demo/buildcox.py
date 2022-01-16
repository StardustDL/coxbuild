import asyncio
from coxbuild.schema import depend, precond, task


@task()
def pre():
    print("pre")


@depend(pre)
@task()
def a():
    print("a")


@depend(pre)
@task()
def b():
    print("b")


@depend(pre)
@task()
async def cost_time():
    print("cost time")
    await asyncio.sleep(0.5)


@precond(lambda: False)
@task()
def ignored():
    raise Exception("Execute ignored task")


@depend(a, b, ignored, cost_time)
@task()
def default():
    pass

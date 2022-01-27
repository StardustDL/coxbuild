import asyncio

from coxbuild.schema import depend, precond, task


@task
def pre():
    print("pre")


@task
def b():
    print("b")


@b.depend
@depend(pre)
@task
def a():
    print("a")


@depend(pre)
@task
async def cost_time():
    print("cost time")
    await asyncio.sleep(0.5)


@task
def ignored():
    pass


@ignored.depend
@precond(lambda: False)
@task
def ignoredByPrecond():
    raise Exception("Execute ignored precond task")


@ignored.depend
@task
def ignoredByBefore():
    raise Exception("Execute ignored before task")


@ignoredByBefore.before
def beforeIgnored(context):
    return False


@depend(a, b, ignored, cost_time)
@task
def default():
    pass

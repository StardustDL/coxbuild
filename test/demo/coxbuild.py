from coxbuild.schema import precond, task, depend, run, before, after, args, kwds


@task()
def pre():
    print("pre")


@depend(pre)
@task()
def a():
    print("a")


@depend(pre)
@task()
def b(*args, **kwds):
    print("b")
    print(args)
    print(kwds)


@before(b)
def beforeB(*args, **kwds):
    print("before b")
    print(args)
    print(kwds)


@after(b)
def afterB(*args, **kwds):
    print("after b")
    print(args)
    print(kwds)


@args(b)
def argsB():
    return [1, 2, 3]


@kwds(b)
def kwdsB():
    return {"x": 1, "y": 2}


@precond(lambda: False)
@task()
def ignored():
    raise Exception("Execute ignored task")


@depend(a, b, ignored)
@task()
def default():
    pass

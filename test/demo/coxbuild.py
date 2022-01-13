from coxbuild.schema import precond, task, depend, run


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


@precond(lambda: False)
@task()
def ignored():
    raise Exception("Execute ignored task")


@depend(a, b, ignored)
@task()
def default():
    pass

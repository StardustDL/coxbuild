from coxbuild.schema import task, depend, run

@task()
def pre():
    print("pre")


@depend(pre)
@task()
def a():
    print("a")
    raise Exception("Try fail")


@depend(pre)
@task()
def b():
    print("b")


@depend(a, b)
@task()
def default():
    pass

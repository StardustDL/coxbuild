from coxbuild.schema import postcond, task, depend, run


@task()
def pre():
    print("pre")


@depend(pre)
@task()
def executeFail():
    raise Exception("Try fail")


@postcond(lambda: False)
@depend(pre)
@task()
def postCondFail():
    pass


@depend(pre)
@task()
def b():
    print("b")


@depend(executeFail, b)
@task()
def default():
    pass


@depend(postCondFail, b)
@task()
def default2():
    pass

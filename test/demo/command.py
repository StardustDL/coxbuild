from coxbuild.schema import task, depend, run


@task()
def echo():
    run(["echo", "Try command invocation."], shell=True)


@depend(echo)
@task()
def git():
    run(["git", "status"])


@depend(git)
@task()
def default():
    pass
from coxbuild.schema import task, depend, run


@task()
def echo():
    run(["echo", "Try command invocation."], shell=True)


@depend(echo)
@task()
def git():
    run(["git", "status"])


@task()
def fail():
    run(["exit", "1"], shell=True)


@task()
def retry():
    run(["exit", "1"], shell=True, retry=3)


@depend(git)
@task()
def default():
    pass

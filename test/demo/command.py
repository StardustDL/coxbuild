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
    run(["cat", "abc.txt"])


@task()
def retry():
    run(["cat", "abc.txt"], retry=3)


@depend(git)
@task()
def default():
    pass

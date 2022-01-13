from coxbuild.schema import group, run

task = group("shell")


@task
def execute(*args, **kwargs):
    run(*args, **kwargs)

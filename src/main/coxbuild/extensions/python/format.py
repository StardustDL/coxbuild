from coxbuild import get_working_directory
from coxbuild.schema import depend, group, precond, run

from . import Settings, task
from .package import hasPackages, upgradePackages

task = group("format", task)


@precond(lambda: not hasPackages({"autopep8": "*", "isort": "*"}))
@task()
def restore():
    upgradePackages("autopep8", "isort")


@task()
def autopep8():
    run(["autopep8", "-r", "--in-place", str(get_working_directory())])


@task()
def isort():
    for file in get_working_directory().glob("**/*.py"):
        if file.is_dir():
            continue
        run(["isort", str(file)])


@depend(autopep8, isort)
@task()
def format():
    pass

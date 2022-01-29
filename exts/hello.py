"""Hello extension"""

__version__ = "0.0.0"

from coxbuild.schema import depend, task


@task
def initial():
    print("Initializing...")


@depend(initial)
@task
def default():
    print("Hello, world!")

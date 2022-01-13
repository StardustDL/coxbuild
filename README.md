![](https://socialify.git.ci/StardustDL/coxbuild/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)

![](https://github.com/StardustDL/coxbuild/workflows/CI/badge.svg) ![](https://img.shields.io/github/license/StardustDL/coxbuild.svg) [![](https://img.shields.io/pypi/dm/coxbuild)](https://pypi.org/project/coxbuild/)

A tiny build automation tool.

## Install

```sh
pip install coxbuild
```

## Usage

### Build Schema

```python
from coxbuild.schema import precond, postcond, task, depend, run, grouptask, invoke # this line can be omitted

@precond(lambda: True)
@postcond(lambda: True)
@task()
def pre():
    print("pre task")


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


@depend(git, pre)
@task()
def default():
    pass
```

### Run

```sh
coxbuild
    [-D <working directory = '.'>]
    [-f <file name = 'coxbuild.py'>]
    [task names = 'default']

# Run default schema and default task
coxbuild
# equivalent to
coxbuild -D . -f coxbuild.py default

# Run in other directory
coxbuild -D path/to/other

# Run using other file
coxbuild -f other.py

# Run specified task
coxbuild task1 task2
```
![](https://socialify.git.ci/StardustDL/coxbuild/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)

![](https://github.com/StardustDL/coxbuild/workflows/CI/badge.svg) ![](https://img.shields.io/github/license/StardustDL/coxbuild.svg) [![](https://img.shields.io/pypi/dm/coxbuild)](https://pypi.org/project/coxbuild/)

Coxbuild is a tiny python-script-based build automation tool, an alternative to make, psake and so on.

> [Documents](https://stardustdl.github.io/coxbuild/)

> [References](https://stardustdl.github.io/coxbuild/api/)

> [Test Coverage Report](https://stardustdl.github.io/coxbuild/cov/)

![](https://raw.githubusercontent.com/StardustDL/coxbuild/master/docs/assets/images/demo.gif)

Supported features:

- Task
- Dependency
- Pre / Post condition
- Lifecycle hooks
  - Setup / Teardown
  - Before / After
- Event-based build as a long-run service
- Multiple schema sources
  - File `file://`
  - Url `url://`
  - Source code `src://`
  - Module `module://`

Extensions:

- Python
- Shell
- Git
- Node.js
- .NET
- Gradle

## Install

```sh
pip install coxbuild
```

## Try

```sh
# Version

coxbuild --version

# Hello World

cb -u https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/hello.py

cb -i src://QHRhc2sKZGVmIGluaXRpYWwoKToKICAgIHByaW50KCJJbml0aWFsaXppbmcuLi4iKQoKCkBkZXBlbmQoaW5pdGlhbCkKQHRhc2sKZGVmIGRlZmF1bHQoKToKICAgIHByaW50KCJIZWxsbywgd29ybGQhIik=

# Life Cycle

cb -u https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/lifecycle.py

# Event-based build

cb -u https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/event.py
```

## Getting Started

> Coxbuild build itself by itself, see [here](https://github.com/StardustDL/coxbuild/blob/master/buildcox.py) for details.

1. Write Schema (buildcox.py)

```python
@task
def pre():
    print("pre task")

@depend(pre)
@task
def default():
    pass
```

2. Run

```sh
coxbuild

# or a shortcut

cb
```

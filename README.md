![](https://socialify.git.ci/StardustDL/coxbuild/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)

[![](https://github.com/StardustDL/coxbuild/workflows/CI/badge.svg)](https://github.com/StardustDL/coxbuild/actions) [![](https://img.shields.io/github/license/StardustDL/coxbuild.svg)](https://github.com/StardustDL/coxbuild/blob/master/LICENSE) [![](https://img.shields.io/pypi/v/coxbuild)](https://pypi.org/project/coxbuild/) [![Downloads](https://pepy.tech/badge/coxbuild?style=flat-square)](https://pepy.tech/project/coxbuild) [![](https://data.jsdelivr.com/v1/package/gh/StardustDL/coxbuild/badge?style=rounded)](https://www.jsdelivr.com/package/gh/StardustDL/coxbuild)

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
  - Module `mod://`
  - Gallery `ext://`

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

cb -e hello

# Life Cycle

cb -u https://cdn.jsdelivr.net/gh/StardustDL/coxbuild@master/demo/lifecycle.py

# Event-based build

cb -u https://cdn.jsdelivr.net/gh/StardustDL/coxbuild@master/demo/event.py
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

## Extensions

We provide a few extensions with coxbuild release package, in `coxbuild.extensions` module. We also provide a gallery of extensions in [exts](https://github.com/StardustDL/coxbuild-ext-gallery/).

> Visit [here](https://stardustdl.github.io/coxbuild/#/extensions/README) for more details.

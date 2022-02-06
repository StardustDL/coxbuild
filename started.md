# Getting Started

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

cb -i ext://hello

cb -i src://QHRhc2sKZGVmIGluaXRpYWwoKToKICAgIHByaW50KCJJbml0aWFsaXppbmcuLi4iKQoKCkBkZXBlbmQoaW5pdGlhbCkKQHRhc2sKZGVmIGRlZmF1bHQoKToKICAgIHByaW50KCJIZWxsbywgd29ybGQhIik=

# Life Cycle

cb -u https://cdn.jsdelivr.net/gh/StardustDL/coxbuild@master/demo/lifecycle.py

# Event-based build

cb -u https://cdn.jsdelivr.net/gh/StardustDL/coxbuild@master/demo/event.py
```

## Usage

Coxbuild build itself by itself, see [here](https://github.com/StardustDL/coxbuild/blob/master/buildcox.py) for details.

### Write Schema

Write in `buildcox.py`.

```python
from coxbuild.schema import task, depend # this line can be omitted

@task
def pre():
    print("pre task")

@depend(pre)
@task
def default():
    pass
```

> Actually, the schema file is also treated as an extension, visit [How It Works](./how-it-works.md) for details.

### Run

```sh
coxbuild
    [-D <working directory = '.'>]
    [-f <file>]
    [-u <url>]
    [-e <extension>]
    [-i <uri = 'file://buildcox.py'>]
    [-c <config entry>]
    [task names = 'default']

# or a shortcut

cb [options]

# Run default schema and default task
coxbuild
# equivalent to
coxbuild -D . -f buildcox.py default

# Run in other directory
coxbuild -D path/to/other

# Run using other file
coxbuild -f other.py

# Run using other url
coxbuild -u url

# Run using extension in gallery
coxbuild -e <extension name>

# Run using specified URI
coxbuild -i uri

# Run specified task
coxbuild task1 task2

# Run with specified configuration entry
coxbuild -c a=1 -c b=2
```

> For valid URI, see [here](extensions/README.md).
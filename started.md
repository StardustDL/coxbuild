# Getting Started

## Install   

```sh
pip install coxbuild
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
    [-i <uri = 'file://buildcox.py'>]
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

# Run using specified URI
coxbuild -i uri

# Run specified task
coxbuild task1 task2
```

> For valid URI, see [here](extensions/README.md).
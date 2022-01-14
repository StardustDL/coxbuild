![](https://socialify.git.ci/StardustDL/coxbuild/image?description=1&font=Bitter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)

![](https://github.com/StardustDL/coxbuild/workflows/CI/badge.svg) ![](https://img.shields.io/github/license/StardustDL/coxbuild.svg) [![](https://img.shields.io/pypi/dm/coxbuild)](https://pypi.org/project/coxbuild/)

Coxbuild is a tiny python-script-based build automation tool, an alternative to make, psake and so on.

![](https://raw.githubusercontent.com/StardustDL/coxbuild/master/docs/demo.gif)

Supported features:

- Task
- Dependency
- Pre / Post condition
- Lifecycle hooks
  - Setup / Teardown
  - Before / After

Extensions:

- Python

## Install

```sh
pip install coxbuild
```

## Usage

Coxbuild build itself by itself, see [here](https://github.com/StardustDL/coxbuild/blob/master/buildcox.py) for details.

### Write Schema

```python
from coxbuild.schema import task, depend # this line can be omitted

@task()
def pre():
    print("pre task")

@depend(pre)
@task()
def default():
    pass
```

### Run

```sh
coxbuild
    [-D <working directory = '.'>]
    [-f <file name = 'buildcox.py'>]
    [task names = 'default']

# Run default schema and default task
coxbuild
# equivalent to
coxbuild -D . -f buildcox.py default

# Run in other directory
coxbuild -D path/to/other

# Run using other file
coxbuild -f other.py

# Run specified task
coxbuild task1 task2
```

## Schema Specification

### Task

Use `task` decorator to define a (named) task.

```python
@task()
def use_function_name_as_task_name(): pass

@task("custom-task-name")
def use_function_name_as_task_name(): pass

# default task
@task()
def default(): pass
```

### Dependency

Use `depend` decorator to define task dependency (you can use full name or instance of the task).

```python
@task()
def t1(): pass

@task("t2")
def t2(): pass

@depend("t1", t2)
@task()
def default(): pass
```

### Group

Use `group` decorator to add namespace to task names (prevent from name conflicting)

```python
ns1task = group("ns1")
ns2task = group("ns2")

# task name: 'ns1:name'
@ns1task()
def name(): pass

# task name: 'ns2:name'
@ns2task()
def name(): pass
```

`group` can be nested.

```python
nstask = group("ns1", group("sub"))

# task name: 'ns1:sub:name'
@nstask()
def name(): pass
```

### Pre/Post Condition

Use `precondition` to decide whether to run the task, and use `postcondition` to check the task works well.

```python
@precond(lambda: True)
@postcond(lambda: True)
@task()
def t(): pass
```

### Before/After Hook

Use `before` hook to do something before task initializing, configure task arguments and decide whether to run the task.
Use `after` hook to do something after task finishing, and check task result.

```python
@before(task1)
def before_task1(context: TaskContext):
    print(context.task.name)
    context.args.extend([1, 2, 3])
    context.kwds.update(a=1, b=2)
    # return False to ignore this task

@after(task1)
def after_task1(context: TaskContext, result: TaskResult):
    pass
```

> Use `before` and `after` decorator with **NO** arguments to hook pipeline events.

Use pipeline `before`/`after` hooks to configure and check all tasks globally.

```python
@before()
def pipeline_before(context: TaskContext):
    if context.task.name != "default":
        context.args.extend(["a", "b", "c"])
        context.kwds.update(p="p")
    # return False to ignore this task

@after()
def pipeline_after(context: TaskContext, result: TaskResult):
    pass
```

### Setup/Teardown

Use `setup` hook to do something before task body.
Use `teardown` hook to do something after task body.
These hooks recieve the same arguments as the task body.

```python
@setup(task2)
def setup_task2(*args, **kwds):
    pass

@teardown(task1)
def teardown_task1(*args, **kwds):
    pass
```

> Use `setup` and `teardown` decorator with **NO** arguments to hook pipeline events.

Use `setup` hook to do something before pipeline, and decide whether to run the pipeline.
Use `teardown` hook to do something after pipeline, and check pipeline result.

```python
@setup()
def setup_pipeline(context: PipelineContext):
    # return False to cancel pipeline
    pass

@teardown()
def teardown_pipeline(context: PipelineContext, result: PipelineResult):
    pass
```

### Lifecycle Events

- Pipeline Setup
  - Task 1
    - Pipeline Before
      - Task Before
        - Task Precondition
          - Task Setup
            - Task Body
          - Task Teardown
        - Task Postcondition
      - Task After
    - Pipeline After
  - Task 2
    - ... (as same as Task 1)
- Pipeline Teardown

Go [here](test/demo/lifecycle.py) to see how to hook these events and how they work.

```sh
# See how lifecycle events occur
coxbuild -D test/demo -f lifecycle.py
```

## Languages

### Python

```python
import coxbuild.extensions.python
import coxbuild.extensions.python.package
```

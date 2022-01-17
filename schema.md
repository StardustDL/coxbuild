
# Schema Specification

## Task

Use `task` decorator to define a (named) task.

```python
@task()
def use_function_name_as_task_name(): pass

@task("custom-task-name")
async def use_custom_name():
    """task document"""
    pass

@task()
async def cost_time():
    print("cost time")
    await asyncio.sleep(0.5)

# default task
@task()
def default(): pass
```

Task can have parameters, see [Before/After Hook](#beforeafter-hook) section for details.

> Do **NOT** use `setup` and `teardown` as task parameter name. These parameter names are used by coxbuild.

Builtin tasks:

| Name     | Description               |
| -------- | ------------------------- |
| `:list`  | List all defined tasks    |
| `:serve` | Start event-based service |

## Dependency

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

## Group

Use `group` decorator to add namespace to task names (prevent from name conflicting).

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

## Pre / Post Condition

Use `precondition` to decide whether to run the task, and use `postcondition` to check the task works well.

```python
@precond(lambda: True)
@postcond(lambda: True)
@task()
def t(): pass
```

## Hooks

### Before / After

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

### Setup / Teardown

Use `setup` hook to do something before task body (in task execution scope).
Use `teardown` hook to do something after task body (in task execution scope, even some exception raises in task body).
These hooks have the same parameters as the task body.

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

### Lifecycle Hooks

> The execution scope in written in parentheses.

- Pipeline Setup (Pipeline)
  - Task 1
    - Pipeline Before (Pipeline)
      - Task Before (Pipeline)
        - Task Precondition (Task)
          - Task Setup (Task)
            - Task Body (Task)
          - Task Teardown (Task)
        - Task Postcondition (Task)
      - Task After (Pipeline)
    - Pipeline After (Pipeline)
  - Task 2
    - ... (as same as Task 1)
- Pipeline Teardown (Pipeline)

Go [here](https://github.com/StardustDL/coxbuild/blob/master/demo/lifecycle.py) to see how to hook these events and how they work.

```sh
# See how lifecycle events occur
coxbuild -D demo -f lifecycle.py
```

## Event

You can schedule some build when event occurs.

Coxbuild provides some builtin events in `coxbuild.events` module, each event return an awaitable iterator, i.e. event generator.

The event handlers are running asynchronously, so use async function and `asyncio.sleep()` instead of sync `time.sleep()`.

```python
from coxbuild.events import repeat, onceevent, once
from coxbuild.events.datetime import attime

@onceevent
async def e():
    print(datetime.now())
    await asyncio.sleep(0.5)

@on(repeat(e, 2))
def do():
    print(datetime.now())
    print("done")

@on(once(attime(datetime.now() + timedelta(seconds=1))))
def do_pipeline_at_next_second():
    pipeline("task1", task2)


@on(delay(timedelta(seconds=1)))
async def async_handler():
    print("before")
    await asyncio.sleep(1)
    print("after")
```

Example for watching filesystem changes, see [here](https://github.com/StardustDL/coxbuild/blob/master/demo/filewatch.py).

To start the long-run service, use builtin task `:serve`.

```sh
coxbuild :serve
```
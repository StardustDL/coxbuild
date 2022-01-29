
# Schema Specification

## Variables

| Name      | Description     |
| --------- | --------------- |
| `manager` | Hosting manager |

## Task

Use `task` decorator to define a task.

```python
@task
def use_function_name_as_task_name(): pass

@named("custom-task-name")
@task
async def use_custom_name():
    """task document"""
    pass

@task
async def cost_time():
    print("cost time")
    await asyncio.sleep(0.5)

# default task
@task
def default(): pass
```

Task can have parameters, see [Before/After Hook](#before-after) section for details.

## Dependency

Use `depend` decorator to define task dependency (you can use full name or instance of the task).

```python
@task
def t1(): pass

@task
def t2(): pass

@depend("t1", t2)
@task
def default(): pass
```

Alternative way.

```python
@task
def default(): pass

@default.depend
@task
def t1(): pass
```

## Group

Use `group` decorator to add namespace to task names (prevent from name conflicting).

```python
# task name: 'ns1:name'
@group("ns1")
@task
def name(): pass

# task name: 'ns2:name'
@group("ns2")
@task
def name(): pass
```

`group` can be nested.

```python
# task name: 'par:sub:name'
@group("par")
@group("sub")
def name(): pass

# task name: 'par:sub:name'
@group("par", "sub")
def name(): pass
```

## Pre / Post Condition

Use `precondition` to decide whether to run the task, and use `postcondition` to check the task works well.

```python
@precond(lambda: True)
@postcond(lambda: True)
@task
def t(): pass
```

Alternative way.

```python
@task
def t(): pass

@t.precond
def pre(): return True

@t.postcond
def post(): return True
```

## Hooks

### Before / After

Use `before` hook to do something before task initializing, configure task arguments and decide whether to run the task.
Use `after` hook to do something after task finishing, and check task result.

```python
def after_task1(context: TaskContext, result: TaskResult):
    pass

@after(after_task1)
@task
def task1():
    pass
```

Alternative way.

```python
@task1.before
def before_task1(context: TaskContext):
    print(context.task.name)
    context.args.extend([1, 2, 3])
    context.kwds.update(a=1, b=2)
    # return False to ignore this task

@task1.after
def after_task1(context: TaskContext, result: TaskResult):
    pass
```

### Setup / Teardown

Use `setup` hook to do something before task body (in task execution scope).
Use `teardown` hook to do something after task body (in task execution scope, even some exception raises in task body).
These hooks have the same parameters as the task body.

```python
def setup_task1(*args, **kwds):
    pass

@setup(setup_task1)
@task
def task1():
    pass
```

Alternative way.

```python
@task2.setup
def setup_task2(*args, **kwds):
    pass

@task1.teardown
def teardown_task1(*args, **kwds):
    pass
```

### Pipeline Hooks

Use pipeline `beforeTask`/`afterTask` hooks to configure and check all tasks globally.

```python
@beforeTask
def pipeline_beforetask(context: TaskContext):
    if context.task.name != "default":
        context.args.extend(["a", "b", "c"])
        context.kwds.update(p="p")
    # return False to ignore this task

@afterTask
def pipeline_aftertask(context: TaskContext, result: TaskResult):
    pass
```

Use pipeline `beforePipeline`/`afterPipeline` hooks to do something before and after pipeline running.

```python
@beforePipeline
def pipeline_before(context: PipelineContext):
    if context.task.name != "default":
        context.args.extend(["a", "b", "c"])
        context.kwds.update(p="p")
    # return False to ignore this task

@afterPipeline
def pipeline_after(context: PipelineContext, result: PipelineResult):
    pass
```

Alternative way.

```python
@pipeline.before
def pipeline_before(context: PipelineContext):
    pass
    # return False to ignore this task

@pipeline.after
def pipeline_after(context: PipelineContext, result: PipelineResult):
    pass
```

### Lifecycle Hooks

> The execution scope in written in parentheses.

- Pipeline Before (Pipeline)
  - Task 1
    - Pipeline Before Task (Pipeline)
      - Task Before (Task)
        - Task Precondition (Task)
          - Task Setup (Task)
            - Task Body (Task)
          - Task Teardown (Task)
        - Task Postcondition (Task)
      - Task After (Task)
    - Pipeline After Task (Pipeline)
  - Task 2
    - ... (as same as Task 1)
- Pipeline After (Pipeline)

Go [here](https://github.com/StardustDL/coxbuild/blob/master/demo/lifecycle.py) to see how to hook these events and how they work.

```sh
# See how lifecycle events occur
coxbuild -D demo -f lifecycle.py
```

## Event

You can schedule some build when event occurs.

Coxbuild provides some builtin events in `coxbuild.events` module, each event return an awaitable iterator, i.e. event generator.

The event handlers are wrapped in a task, and running asynchronously, so use async function and `asyncio.sleep()` instead of sync `time.sleep()`.

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
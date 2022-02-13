# Library

> [References](https://stardustdl.github.io/coxbuild/api/)

## Manager

Use **Manager** to manage extensions, configurations and execute tasks.

```python
from coxbuild.managers import Manager

manager: Manager

manager.register(ext1)
manager.configBuilders.add(configBuilder1)

manager.execute("task1")
```

## Task

Use **Task** to do something and get result with running metadata (exception, duration, and so on).

```python
task: Task

# execute task individually (no pipeline, without dependencies and registered hooks)

result = await task(*args, **kwds)
```

## Pipeline

Use **Pipeline** to run managed tasks with dependencies and hooks.

You can access the default pipeline by variable `pipeline` in schema.

```python
pipeline: Pipeline

tasklist: list[Task|str] = [task1, "task2"]

# execute tasks and their dependencies

result = await pipeline(*tasklist)
```

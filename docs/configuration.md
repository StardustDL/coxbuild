# Configuration

Coxbuild use `Configuration` class to store configuration data. You can use `context.config` to access the configuration.

> Configuration data is a key-value pair. The key is a case-insensitive string, and the value can be any type. Coxbuild use `:` in key to split configuration sections.

```python
@beforePipeline
def initialize(context: PipelineContext):
    config = context.config
    config["a"] = 1
```

Also you can use `-c` option to specify configuration entry:

```sh
coxbuild -c a=1 -c b=2
```

Since many settings provider is inherited from `ConfigurationAccessor`, then many configuration entries have a fallback (with prefix `coxbuild:`) in environment variables. For example `project:src` has fallback environment variable `coxbuild:project:src`.

## Project Settings

`ProjectSettings` class provide shared general configuration for projects.

```python
from coxbuild.extensions import ProjectSettings

@beforePipeline
def initialize(context: PipelineContext):
    project = ProjectSettings(context.config)
    project.src = Path("path/to/src")
```
